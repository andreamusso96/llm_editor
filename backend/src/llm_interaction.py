import json
import os
from typing import Type, TypeVar, Optional, Literal
from pydantic import BaseModel, ValidationError
import google.generativeai as genai
import time

from src.utils import logger
from config import GOOGLE_API_KEY

# Define a generic type for Pydantic models
T = TypeVar('T', bound=BaseModel)

class LLMInteraction:
    def __init__(self, model_name: str, max_retries: int = 3, retry_delay: int = 3):
        """
        Initializes the LLM Interaction Module with a specific Gemini model,
        configured for JSON output.

        Args:
            model_name (str): The name of the Gemini model to use (e.g., "gemini-pro", "gemini-1.5-flash").
        """
        self.model_name = model_name
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        genai.configure(api_key=GOOGLE_API_KEY)
        # Configure the model to expect and output JSON.
        self.model = genai.GenerativeModel(
            self.model_name,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
        )

    def _get_raw_llm_output(self, prompt: str) -> str | None:
        """
        Gets a raw string output (expected to be JSON) from the Gemini LLM.
        """
        current_retries = 0

        while current_retries < self.max_retries:
            try:
                response = self.model.generate_content(prompt)
                
                if response.parts:
                    return response.text
                else:
                    if response.prompt_feedback and response.prompt_feedback.block_reason:
                        logger.warning(f"Prompt blocked due to: {response.prompt_feedback.block_reason_message}")
                        return None
                    else:
                        logger.warning(f"Gemini response has no parts but no block reason. Full response: {response}")
                        if current_retries == self.max_retries:
                            logger.error(f"Failed to get raw output from LLM after {self.max_retries} retries")
                            return None
            except Exception as e:
                logger.error(f"Error during Gemini API call: {e}")
                if current_retries == self.max_retries:
                    logger.error(f"Failed to get raw output from LLM after {self.max_retries} retries")
                    return None
                
            current_retries += 1
            if current_retries < self.max_retries:
                logger.warning(f"Retrying LLM call after {self.retry_delay} seconds")
                time.sleep(self.retry_delay)

        logger.error(f"Failed to get raw output from LLM after {self.max_retries} retries")
        return None

    def get_validated_response(self, prompt: str, response_model: Type[T]) -> Optional[T]:
        """
        Gets a response from the LLM, parses it as JSON, and validates it
        against the provided Pydantic model.

        Args:
            prompt: The prompt string to send to the LLM. This prompt should
                    guide the LLM to generate JSON that matches the response_model.
            response_model: The Pydantic model to validate the response against.

        Returns:
            An instance of the Pydantic model if successful, None otherwise.
        """
        raw_output = self._get_raw_llm_output(prompt)
        if raw_output is None:
            logger.error(f"Failed to get raw output from LLM after {self.max_retries} retries")
            return None

        try:
            # Parse the raw output as JSON
            # The Gemini API with response_mime_type="application/json" should already return a JSON string.
            # Pydantic's model_validate_json can directly parse the JSON string.
            validated_data = response_model.model_validate_json(raw_output)
            return validated_data
        except json.JSONDecodeError as e: # Should be less common if Gemini respects mime_type
            logger.error(f"Error: Failed to decode LLM output as JSON. Details: {e}")
            return None
        except ValidationError as e:
            logger.error(f"Error: LLM output validation failed. Details: {e}")
            return None 