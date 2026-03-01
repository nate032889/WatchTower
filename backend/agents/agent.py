from typing import Type, Dict
from agents.base import BaseLLMAgent
from agents.gemini import GeminiAgent
# from agents.openai import ChatGPTAgent
from agents.types import LLMProvider


def get_llm_agent(provider: LLMProvider) -> BaseLLMAgent:
    """Factory to instantiate the requested LLM agents."""

    # Map the Enum directly to the class Type
    providers: Dict[LLMProvider, Type[BaseLLMAgent]] = {
        LLMProvider.GEMINI: GeminiAgent,
        # LLMProvider.CHATGPT: ChatGPTAgent,
        # LLMProvider.CLAUDE: ClaudeAgent
    }

    agent_class = providers.get(provider)
    if not agent_class:
        # This is strictly an internal safeguard; the serializer prevents this from happening.
        raise ValueError(f"Implementation for provider '{provider.value}' not found.")

    return agent_class()