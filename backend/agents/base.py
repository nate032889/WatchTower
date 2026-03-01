from abc import ABC, abstractmethod
from typing import List
from api.models import Message # Import the Django model

class BaseLLMAgent(ABC):
    @abstractmethod
    def generate_response(self, prompt: str, history: List[Message] = None) -> str:
        """
        Takes a prompt string and optional conversation history of Message objects,
        and returns the LLM's string response.
        """
        pass
