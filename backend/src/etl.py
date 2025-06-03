from src.models import Prompt, InputGranularityEnum
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import yaml
import os
from config import PROJECT_DIR


class ETLService:
    def __init__(self, db: Session):
        self.db = db
        self.prompt_dir = os.path.join(PROJECT_DIR, "database_setup/prompts/")
        self.prompt_files = [
            "mc_closkey.yml"
        ]

    def _load_prompts_from_yaml(self) -> List[Dict[str, Any]]:
        for file in self.prompt_files:
            with open(os.path.join(self.prompt_dir, file), 'r') as file:
                prompts = yaml.safe_load(file)
        return prompts
    

    def load_prompts_from_yaml_to_db(self):
        prompts = self._load_prompts_from_yaml()

        for prompt in prompts:
            prompt_model = Prompt(
                prompt_id_ref=prompt['prompt_id_ref'],
                description=prompt['description'],
                input_granularity=InputGranularityEnum(prompt['input_granularity']),
                text=prompt['prompt']
            )
            self.db.add(prompt_model)
        self.db.commit()
    