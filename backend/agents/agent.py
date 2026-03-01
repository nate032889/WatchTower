from typing import Type, Dict, Optional
from agents.base import BaseLLMAgent
from agents.gemini import GeminiAgent
# from agents.openai import ChatGPTAgent
from agents.types import LLMProvider


def get_llm_agent(provider: LLMProvider, api_key: Optional[str] = None) -> BaseLLMAgent:
    """
    Factory to instantiate the requested LLM agents.
    :param provider: The enum value of the provider (e.g., 'gemini').
    :param api_key: The specific API key to use for this instance.
    """

    # Map the Enum directly to the class Type
    providers: Dict[LLMProvider, Type[BaseLLMAgent]] = {
        LLMProvider.GEMINI: GeminiAgent,
        # LLMProvider.CHATGPT: ChatGPTAgent,
        # LLMProvider.CLAUDE: ClaudeAgent
    }

    agent_class = providers.get(provider)
    if not agent_class:
        raise ValueError(f"Implementation for provider '{provider.value}' not found.")

    # Instantiate the agent, passing the API key if provided
    return agent_class(api_key=api_key)
