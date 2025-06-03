# (Typically in a schemas.py or similar file)
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Callable
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from src.llm_interaction import LLMInteraction
from src.utils import logger
from src.models import Correction, CorrectionStep, AnalysisResult, CorrectionStatusEnum, Prompt, InputGranularityEnum
from src.tasks import process_correction_step_task
from src.schemas import RichSegment, RichSegmentIssue, CorrectionStatusResponse, CorrectionResultResponse, CorrectionCreateResponse
from src.text_utils import split_text_into_paragraphs


class DummyBackgroundTasks:
    def add_task(self, task: Callable, *args, **kwargs):
        task(*args, **kwargs)

class BackgroundTaskQueue:
    def __init__(self, background_tasks: BackgroundTasks | DummyBackgroundTasks):
        self.queue = []
        self.background_tasks = background_tasks
    
    def add_task(self, task: Callable, *args, **kwargs):
        self.queue.append((task, args, kwargs))
    
    def process_queue(self):
        for task, args, kwargs in self.queue:
            self.background_tasks.add_task(task, *args, **kwargs)
        

class CorrectionService:
    def __init__(self, db: Session, llm_model_name: str):
        self.db = db
        self.llm = LLMInteraction(model_name=llm_model_name)

    def create_new_correction(self, original_text: str, prompt_id_refs: List[str], background_tasks: BackgroundTasks | DummyBackgroundTasks) -> CorrectionCreateResponse:
        logger.debug(f"Creating new correction for {original_text} with prompts {prompt_id_refs}")
        new_correction = Correction(original_text=original_text, status=CorrectionStatusEnum.pending)
        self.db.add(new_correction)
        self.db.flush()
        self.db.refresh(new_correction)

        bg_task_queue = BackgroundTaskQueue(background_tasks)
        for prompt_id_ref in prompt_id_refs:
            logger.debug(f"Creating new correction step for prompt {prompt_id_ref}")

            prompt = self.db.query(Prompt).filter(Prompt.prompt_id_ref == prompt_id_ref, Prompt.is_enabled == True).first()
            if not prompt:
                logger.error(f"Prompt with id_ref {prompt_id_ref} not found")
                raise ValueError(f"Prompt with id_ref {prompt_id_ref} not found")
            
            if prompt.input_granularity == InputGranularityEnum.whole_text:
                correction_step = CorrectionStep(correction_id=new_correction.correction_id, 
                                                 prompt_id=prompt.prompt_id, 
                                                 input_text_sent_to_llm=original_text, 
                                                 original_text_start_char=0,
                                                 paragraph_index=None, 
                                                 status=CorrectionStatusEnum.pending)
                self.db.add(correction_step)
                self.db.flush()
                
                bg_task_queue.add_task(
                    process_correction_step_task, 
                    correction_step_id=correction_step.correction_step_id, 
                    llm_model_name=self.llm.model_name)
            
            elif prompt.input_granularity == InputGranularityEnum.paragraph:
                paragraphs_with_offsets = split_text_into_paragraphs(original_text)

                for idx, (paragraph, start_offset) in enumerate(paragraphs_with_offsets):
                    # skip empty paragraphs
                    if not paragraph.strip():
                        continue
                        
                    correction_step = CorrectionStep(correction_id=new_correction.correction_id, 
                                                    prompt_id=prompt.prompt_id, 
                                                    input_text_sent_to_llm=paragraph, 
                                                    original_text_start_char=start_offset,
                                                    paragraph_index=idx, 
                                                    status=CorrectionStatusEnum.pending)
                    self.db.add(correction_step)
                    self.db.flush()
                    self.db.refresh(correction_step)

                    bg_task_queue.add_task(
                            process_correction_step_task, 
                            correction_step_id=correction_step.correction_step_id, 
                            llm_model_name=self.llm.model_name)


        self.db.commit()
        bg_task_queue.process_queue()
        return CorrectionCreateResponse(correction_id=new_correction.correction_id)
    

    def get_correction_status(self, correction_id: int) -> CorrectionStatusResponse:
        correction = self.db.query(Correction).filter(Correction.correction_id == correction_id).first()
        if not correction:
            logger.error(f"Correction with id {correction_id} not found")
            raise ValueError(f"Correction with id {correction_id} not found")
        
        total_steps = self.db.query(CorrectionStep).filter(CorrectionStep.correction_id == correction_id).count()
        completed_steps = self.db.query(CorrectionStep).filter(CorrectionStep.correction_id == correction_id, CorrectionStep.status == CorrectionStatusEnum.completed).count()
        return CorrectionStatusResponse(correction_id=correction.correction_id, status=correction.status.value, progress=completed_steps / total_steps if total_steps > 0 else 0)
    
    def get_correction_results(self, correction_id: int) -> CorrectionResultResponse:
        correction = self.db.query(Correction).filter(Correction.correction_id == correction_id).first()
        
        if not correction:
            logger.error(f"Correction with id {correction_id} not found")
            raise ValueError(f"Correction with id {correction_id} not found")
        
        if correction.status != CorrectionStatusEnum.completed:
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