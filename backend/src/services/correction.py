from typing import List, Callable
from sqlalchemy.orm import Session
import jinja2
import asyncio

from src.services.llm_interaction import LLMInteraction
from src.utils import logger, get_db_context
from src.models import Correction, CorrectionStep, AnalysisResult, CorrectionStatusEnum, Prompt, InputGranularityEnum
from src.schemas.schemas_api import RichSegment, RichSegmentIssue, CorrectionStatusResponse, CorrectionResultResponse, CorrectionCreateResponse
from src.schemas.schemas_llm import SnippetIssuesRevisionList
from src.services.text_utils import split_text_into_paragraphs, locate_snippet_in_segment


class CorrectionService:
    def __init__(self, db: Session, llm_model_name: str):
        self.db = db
        self.llm = LLMInteraction(model_name=llm_model_name)

    def create_new_correction(self, original_text: str, prompt_id_refs: List[str]) -> CorrectionCreateResponse:
        logger.debug(f"Initiating correction for {original_text} with prompts {prompt_id_refs}")
        new_correction = Correction(original_text=original_text, status=CorrectionStatusEnum.PENDING)
        self.db.add(new_correction)
        self.db.commit()
        self._add_correction_steps(correction_id=new_correction.correction_id, prompt_id_refs=prompt_id_refs, original_text=original_text)
        self.db.commit()
        return CorrectionCreateResponse(correction_id=new_correction.correction_id)

            
    def _add_correction_steps(self, correction_id: int, prompt_id_refs: List[str], original_text: str):
        for prompt_id_ref in prompt_id_refs:
            base_prompt = self.db.query(Prompt).filter(Prompt.prompt_id_ref == prompt_id_ref, Prompt.is_enabled == True).first()
            if base_prompt.input_granularity == InputGranularityEnum.WHOLE_TEXT:
                correction_step = CorrectionStep(correction_id=correction_id, 
                                                 prompt_id=base_prompt.prompt_id, 
                                                 input_text_sent_to_llm=original_text, 
                                                 original_text_start_char=0,
                                                 paragraph_index=None, 
                                                 status=CorrectionStatusEnum.PENDING)
                self.db.add(correction_step)
    
            elif base_prompt.input_granularity == InputGranularityEnum.PARAGRAPH:
                paragraphs_with_offsets = split_text_into_paragraphs(original_text)
                for idx, (paragraph, start_offset) in enumerate(paragraphs_with_offsets):
                    if not paragraph.strip():
                        continue

                    correction_step = CorrectionStep(correction_id=correction_id, 
                                                    prompt_id=base_prompt.prompt_id, 
                                                    input_text_sent_to_llm=paragraph, 
                                                    original_text_start_char=start_offset,
                                                    paragraph_index=idx, 
                                                    status=CorrectionStatusEnum.PENDING)
                    self.db.add(correction_step)

    async def run_correction(self, correction_id: int):
        correction = self.db.query(Correction).filter(Correction.correction_id == correction_id).first()
        llm_step_coroutines = self._get_llm_coroutines(correction=correction)
        # It runs the LLM calls in parallel. Return exceptions just makes sures that it continues running even if one of the LLM calls fails.
        await asyncio.gather(*llm_step_coroutines, return_exceptions=True)
        self._construct_analysis_results(correction_id=correction_id)
        correction.status = CorrectionStatusEnum.COMPLETED
        self.db.commit()


    def _get_llm_coroutines(self, correction: Correction):
        llm_calls = []
        for step in correction.steps:
            input_text = step.input_text_sent_to_llm
            prompt = jinja2.Template(step.prompt.text).render(
                input_text=input_text
            )
            llm_coro = self.llm.get_validated_response(
                prompt=prompt,
                response_model=SnippetIssuesRevisionList
            )

            llm_calls.append(self._run_llm_step(correction_step_id=step.correction_step_id, llm_coroutine=llm_coro))

        return llm_calls

    async def _run_llm_step(self, correction_step_id: int, llm_coroutine: Callable):
        try: 
            result = await llm_coroutine
        except Exception as e:
            with get_db_context() as db:
                logger.error(f"Error running LLM step {correction_step_id}: {e}")
                correction_step = db.query(CorrectionStep).filter(CorrectionStep.correction_step_id == correction_step_id).first()
                correction_step.status = CorrectionStatusEnum.FAILED
                db.commit()
                return
        
        with get_db_context() as db:
            correction_step = db.query(CorrectionStep).filter(CorrectionStep.correction_step_id == correction_step_id).first()
            correction_step.llm_response = result.model_dump()
            correction_step.status = CorrectionStatusEnum.COMPLETED
            db.commit()


    def _construct_analysis_results(self, correction_id: int):
        with get_db_context() as db:
            correction = db.query(Correction).filter(Correction.correction_id == correction_id).first()
            for step in correction.steps:
                if step.status == CorrectionStatusEnum.COMPLETED:
                    issues = step.llm_response['issues']
                    for issue_item in issues:
                        start_char, end_char = locate_snippet_in_segment(
                            segment_text=step.input_text_sent_to_llm,
                            segment_global_start_offset=step.original_text_start_char,
                            snippet=issue_item["snippet"],
                            sentence_context=issue_item["sentence_context"]
                        )

                        analysis_result = AnalysisResult(
                            correction_step_id=step.correction_step_id,
                            snippet=issue_item["snippet"],
                            issue=issue_item["issue"],
                            revision=issue_item["revision"],
                            original_text_start_char=start_char,
                            original_text_end_char=end_char
                        )

                        db.add(analysis_result)

    def get_correction_status(self, correction_id: int) -> CorrectionStatusResponse:
        correction = self.db.query(Correction).filter(Correction.correction_id == correction_id).first()
        total_steps = len(correction.steps)
        completed_steps = len([step for step in correction.steps if step.status in [CorrectionStatusEnum.COMPLETED, CorrectionStatusEnum.FAILED]])
        progress = completed_steps / total_steps if total_steps > 0 else 0
        return CorrectionStatusResponse(correction_id=correction.correction_id, status=correction.status.value, progress=progress)

    def get_correction_results(self, correction_id: int) -> CorrectionResultResponse:
        correction = self.db.query(Correction).filter(Correction.correction_id == correction_id).first()
        
        if not correction:
            logger.error(f"Correction with id {correction_id} not found")
            raise ValueError(f"Correction with id {correction_id} not found")
        
        if correction.status != CorrectionStatusEnum.COMPLETED:
            return CorrectionResultResponse(correction_id=correction.correction_id, 
                                            original_text=correction.original_text, 
                                            status=correction.status.value, 
                                            rich_segments=None)
        
        analysis_items = []
        for step in correction.steps:
            analysis_items.extend(step.analysis_results)
        
        if not analysis_items:
            return CorrectionResultResponse(
                correction_id=correction.correction_id, 
                original_text=correction.original_text, 
                status=correction.status.value, 
                rich_segments=[RichSegment(text=correction.original_text, start_char=0, end_char=len(correction.original_text), issues=[])]
            )
        
        original_text = correction.original_text
        points = {0, len(original_text)}
        for item in analysis_items:
            if item.original_text_start_char is not None and item.original_text_end_char >= 0 and item.original_text_start_char < item.original_text_end_char:
                points.add(item.original_text_start_char)
                points.add(item.original_text_end_char)

        # Sort and ensure points are unique and create valid segments
        unique_sorted_points = sorted(list(points))

        rich_segments = [] 
        for i in range(len(unique_sorted_points) - 1):
            start_char = unique_sorted_points[i]
            end_char = unique_sorted_points[i + 1]
            
            segment_text = original_text[start_char:end_char]
            issues_for_segment = []
            for item in analysis_items:
                if item.original_text_start_char <= start_char and item.original_text_end_char >= end_char:
                    issues_for_segment.append(RichSegmentIssue(prompt_id_ref=item.correction_step.prompt.prompt_id_ref, 
                                                               issue=item.issue, 
                                                               revision=item.revision))


            rich_segments.append(RichSegment(text=segment_text, start_char=start_char, end_char=end_char, issues=issues_for_segment))

        rich_segments.sort()
        return CorrectionResultResponse(correction_id=correction.correction_id, 
                                        original_text=correction.original_text, 
                                        status=correction.status.value, 
                                        rich_segments=rich_segments)