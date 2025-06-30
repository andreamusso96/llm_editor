from typing import Type, TypeVar, Optional
from pydantic import BaseModel
import google.genai as genai
import asyncio

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
        self.client = genai.Client(api_key=GOOGLE_API_KEY)

    async def get_validated_response(self, prompt: str, response_model: Type[T]) -> Optional[T]:
        """
        Gets a raw string output (expected to be JSON) from the Gemini LLM.
        """
        current_retries = 0

        while current_retries < self.max_retries:
            try:
                config = {
                    "response_mime_type": "application/json",
                    "response_schema": response_model
                }
                response = await self.client.aio.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config
                )

                if response.parsed:
                    return response.parsed
                else:
                    raise ValueError("No response from LLM")
                
            except Exception as e:
                logger.error(f"Error during Gemini API call: {e}")
                if current_retries == self.max_retries:
                    logger.error(f"Failed to get raw output from LLM after {self.max_retries} retries")
                    return None
                
            current_retries += 1
            if current_retries < self.max_retries:
                logger.warning(f"Retrying LLM call after {self.retry_delay} seconds")
                await asyncio.sleep(self.retry_delay)

        logger.error(f"Failed to get raw output from LLM after {self.max_retries} retries")
        return None