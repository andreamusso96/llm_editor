from pydantic import BaseModel, Field
from typing import List as PyList, Optional # Renamed to PyList to avoid conflict if List from typing is used differently
import jinja2
from sqlalchemy.orm import Session

from src.llm_interaction import LLMInteraction
from src.models import CorrectionStep, AnalysisResult, Correction
from src.models import CorrectionStatusEnum
from src.utils import logger, get_db_context
from src.text_utils import locate_snippet_in_segment

class SnippetIssueRevision(BaseModel):
    snippet: str
    issue: str
    revision: str

class SnippetIssuesRevisionList(BaseModel):
    issues: PyList[SnippetIssueRevision]


def process_correction_step_task(correction_step_id: int, llm_model_name: str):
    logger.debug(f"Task started for CorrectionStep ID: {correction_step_id}")
    llm_service = LLMInteraction(model_name=llm_model_name)

    with get_db_context() as db:
        try: 
            step = db.query(CorrectionStep).filter(CorrectionStep.correction_step_id == correction_step_id).first()

            if not step:
                logger.error(f"CorrectionStep with ID {correction_step_id} not found")
                raise ValueError(f"CorrectionStep with ID {correction_step_id} not found")
            
            step.status = CorrectionStatusEnum.processing
            db.commit()
            db.refresh(step)

            prompt = jinja2.Template(step.prompt.text).render(
                input_text=step.input_text_sent_to_llm,
            )
            logger.debug(f"Generated prompt for step {correction_step_id}: {prompt[:200]}...")

            llm_response = llm_service.get_validated_response(
                prompt=prompt,
                response_model=SnippetIssuesRevisionList
            )

            if not llm_response:
                step.status = CorrectionStatusEnum.failed
                step.llm_response = None
                step.error_message = "No response from LLM"
                db.commit()
            
            else:
                logger.debug(f"Processing {len(llm_response.issues)} issues from LLM for step {correction_step_id}")
                for issue_item in llm_response.issues:
                    start_char, end_char = locate_snippet_in_segment(
                        segment_text=step.input_text_sent_to_llm,
                        segment_global_start_offset=step.original_text_start_char,
                        snippet=issue_item.snippet
                    )
                    logger.debug(f"Located snippet at positions {start_char}:{end_char} for step {correction_step_id}")

                    analysis_result = AnalysisResult(
                        correction_step_id=step.correction_step_id,
                        snippet=issue_item.snippet,
                        issue=issue_item.issue,
                        revision=issue_item.revision,
                        original_text_start_char=start_char,
                        original_text_end_char=end_char
                    )

                    db.add(analysis_result)
                
                step.llm_response = llm_response.model_dump()
                step.status = CorrectionStatusEnum.completed
                db.commit()

                logger.debug(f"CorrectionStep {correction_step_id} completed successfully with {len(llm_response.issues)} issues found")

        except Exception as e:
            logger.error(f"Error processing CorrectionStep {correction_step_id}: {str(e)}", exc_info=True)
            step.status = CorrectionStatusEnum.failed
            step.error_message = str(e)
            db.commit()
        
        finally:
            try_finalize_correction_status(correction_id=step.correction_id, db=db)


def try_finalize_correction_status(correction_id: int, db: Session):
    correction = db.query(Correction).filter(Correction.correction_id == correction_id).first()
    if not correction:
        logger.error(f"Correction with ID {correction_id} not found")
        raise ValueError(f"Correction with ID {correction_id} not found")
    
    step_statuses = [step.status for step in correction.steps]
    is_job_finished = all(status in [CorrectionStatusEnum.completed, CorrectionStatusEnum.failed] for status in step_statuses)

    if is_job_finished:
        correction.status = CorrectionStatusEnum.completed
        db.commit()
        logger.debug(f"Correction {correction_id} completed successfully")
    else:
        correction.status = CorrectionStatusEnum.processing
        db.commit()
        logger.debug(f"Correction {correction_id} is still processing")