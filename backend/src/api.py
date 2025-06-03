from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status as http_status
from sqlalchemy.orm import Session
from typing import List

# Assuming your modules are structured like this
from config import LLM_MODEL_NAME
from src.utils import get_db, logger # Your DB session dependency and logger
from src.correction import CorrectionService # Your service layer
from src.llm_interaction import LLMInteraction
from src.schemas import ( # Your Pydantic models
    CorrectionCreateRequest, CorrectionCreateResponse,
    CorrectionStatusResponse, CorrectionResultResponse, PromptList, Prompt
)
from src.models import Prompt as PromptModel

LLM_MODEL_NAME = "gemini-1.5-flash"

router = APIRouter(
    prefix="/api/v1", # Base prefix for this router
    tags=["corrections"] # Tag for OpenAPI docs
)

@router.post("/corrections",
             response_model=CorrectionCreateResponse,
             summary="Submit text for correction and initiate processing")
async def create_correction_submission(
    request_data: CorrectionCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db) 
):
    """
    Submits a piece of text and a list of prompt IDs for correction.
    The processing is done in the background.
    """
    logger.debug(f"Received correction request for {len(request_data.prompt_id_refs)} prompts.")
    correction_service = CorrectionService(db=db, llm_model_name=LLM_MODEL_NAME)
    correction_create_response = correction_service.create_new_correction(
        original_text=request_data.text_content,
        prompt_id_refs=request_data.prompt_id_refs,
        background_tasks=background_tasks
    )
    if not correction_create_response:
        logger.error("Failed to create correction submission.")
        raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to initiate correction process.")
    return correction_create_response


@router.get("/corrections/{correction_id}/status",
            response_model=CorrectionStatusResponse,
            summary="Get the status of a correction job")
async def get_correction_job_status(
    correction_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieves the current status and progress of a correction job.
    """
    logger.debug(f"Fetching status for submission_id: {correction_id}")
    correction_service = CorrectionService(db=db, llm_model_name=LLM_MODEL_NAME)
    status_data = correction_service.get_correction_status(correction_id=correction_id)
    if not status_data:
        logger.warning(f"Status requested for non-existent correction_id: {correction_id}")
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Correction ID not found.")
    return status_data


@router.get("/corrections/{correction_id}/results",
            response_model=CorrectionResultResponse,
            summary="Get the results of a completed correction job")
async def get_correction_job_results(
    correction_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieves the processed results for a correction job, including rich text segments.
    """
    logger.debug(f"Fetching results for correction_id: {correction_id}")
    correction_service = CorrectionService(db=db, llm_model_name=LLM_MODEL_NAME)
    result_data = correction_service.get_correction_results(correction_id=correction_id)
    if not result_data:
        logger.warning(f"Results requested for non-existent correction_id: {correction_id}")
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Correction ID not found.")
    return result_data

@router.get("/prompts",
            response_model=PromptList,
            summary="List all available and enabled prompts")
async def list_available_prompts(
    db: Session = Depends(get_db) 
):
    """
    Returns a list of all prompts that are currently enabled and can be used for corrections.
    """
    logger.debug("Fetching list of available prompts.")
    prompts = db.query(PromptModel).filter(PromptModel.is_enabled == True).all()
    return PromptList(prompts=[Prompt(prompt_id_ref=prompt.prompt_id_ref, prompt_description=prompt.description) for prompt in prompts])