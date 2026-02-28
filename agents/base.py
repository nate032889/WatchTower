from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseLLMAgent(ABC):
    @abstractmethod
    def generate_response(self, prompt: str, history: List[Dict[str, Any]] = None) -> str:
        """
        Takes a prompt string and optional conversation history,
        and returns the LLM's string response.
        """
        pass
