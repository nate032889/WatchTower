import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from agents.base import BaseLLMAgent
from api.models import Message

logger = logging.getLogger(__name__)

# Read the system prompt from the file at module load time for efficiency.
try:
    SYSTEM_PROMPT_PATH = Path(__file__).parent / "system_prompt.md"
    with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    logger.error("system_prompt.md not found! The agent will not have its initial instructions.")
    SYSTEM_PROMPT = "" 

class GeminiAgent(BaseLLMAgent):
    def __init__(self, model_name: str = "models/gemini-2.5-flash", api_key: Optional[str] = None):
        """
        Initializes the Gemini client.
        :param api_key: Optional API key. If not provided, falls back to env var.
        """
        # Use the provided key, or fall back to the environment variable
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("Gemini API key not found. Please provide it or set GEMINI_API_KEY.")

        genai.configure(api_key=self.api_key)

        self.model = genai.GenerativeModel(
            model_name,
            system_instruction=SYSTEM_PROMPT
        )

    def _format_history(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """
        Private helper to translate Django Message objects into the Gemini API format.
        """
        sdk_history = []
        if messages:
            for msg in messages:
                sdk_history.append({'role': msg.role, 'parts': [msg.content]})
        return sdk_history

    def generate_response(self, prompt: str, history: List[Message] = None) -> str:
        """
        Sends a prompt to the Gemini API as part of a conversation and returns the text response.
        """
        try:
            sdk_history = self._format_history(history)
            chat_session = self.model.start_chat(history=sdk_history)
            response = chat_session.send_message(prompt)
            return response.text

        except (google_exceptions.GoogleAPICallError, google_exceptions.RetryError) as e:
            logger.error(f"Gemini API call failed: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred in GeminiAgent: {e}")
            raise
