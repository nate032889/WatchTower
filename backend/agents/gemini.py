import os
import logging
from pathlib import Path
import google.generativeai as genai
from google.generativeai.types import content_types
from google.api_core import exceptions as google_exceptions
from agents.base import BaseLLMAgent
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Read the system prompt from the file at module load time for efficiency.
try:
    SYSTEM_PROMPT_PATH = Path(__file__).parent / "system_prompt.md"
    with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    logger.error("system_prompt.md not found! The agent will not have its initial instructions.")
    SYSTEM_PROMPT = "" # Fallback to an empty string

class GeminiAgent(BaseLLMAgent):
    def __init__(self, model_name: str = "models/gemini-2.5-flash"):
        """
        Initializes the Gemini client, configuring it with the system prompt.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not found.")

        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel(
            model_name,
            system_instruction=SYSTEM_PROMPT
        )

    def generate_response(self, prompt: str, history: List[Dict[str, Any]] = None) -> str:
        """
        Sends a prompt to the Gemini API as part of a conversation and returns the text response.
        """
        try:
            # The history needs to be converted to the SDK's expected format.
            sdk_history = [content_types.to_content(item) for item in history] if history else []

            chat_session = self.model.start_chat(history=sdk_history)
            response = chat_session.send_message(prompt)
            return response.text

        except (google_exceptions.GoogleAPICallError, google_exceptions.RetryError) as e:
            logger.error(f"Gemini API call failed: {e}")
            raise  # Re-raise for the service layer to handle
        except Exception as e:
            logger.error(f"An unexpected error occurred in GeminiAgent: {e}")
            raise
