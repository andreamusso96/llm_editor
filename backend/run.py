import asyncio

def test_etl():
    from src.etl.etl import ETLServiceMia
    from src.utils import get_db_context, init_db, engine
    from src.models import Base
    Base.metadata.drop_all(bind=engine)
    init_db()
    with get_db_context() as db:
        etl_service = ETLServiceMia(db)
        etl_service.load_prompts_from_yaml_to_db()


async def test_correction():
    from src.services.correction import CorrectionService
    from src.utils import get_db_context
    from src.models import Prompt
    text_path = '/Users/andrea/Desktop/PhD/llm_editor/frontend/public/text.txt'
    with open(text_path, 'r') as file:
        text = file.read()

    with get_db_context() as db:
        prompt_ids = db.query(Prompt).filter(Prompt.is_enabled == True).all()
        prompt_id_refs = [prompt.prompt_id_ref for prompt in prompt_ids[:3]]

        correction_service = CorrectionService(db, llm_model_name="gemini-1.5-flash-8b")
        response = correction_service.create_new_correction(original_text=text, prompt_id_refs=prompt_id_refs)
        await correction_service.run_correction(correction_id=response.correction_id)
        correction_service.get_correction_status(correction_id=response.correction_id)
        correction_service.get_correction_results(correction_id=response.correction_id)


if __name__ == "__main__":
    test_etl()
    asyncio.run(test_correction())