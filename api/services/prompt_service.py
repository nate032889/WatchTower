import logging
from agents.agent import get_llm_agent
from agents.types import LLMProvider, ServiceResult
from api.serializers.prompt import PromptSerializer

logger = logging.getLogger(__name__)


class PromptService:
    @staticmethod
    def process_prompt_request(request_data) -> ServiceResult:
        """
        Handles the entire process of validating a prompt request,
        executing it, and returning a ServiceResult.
        """
        serializer = PromptSerializer(data=request_data)
        if not serializer.is_valid():
            return ServiceResult(
                success=False,
                error_message=str(serializer.errors),
                status_code=400
            )

        validated_data = serializer.validated_data
        prompt = validated_data['prompt']
        provider = LLMProvider(validated_data['provider'])
        history = validated_data.get('history', []) # Get history or default to empty list

        try:
            # Initialization & Execution
            agent = get_llm_agent(provider)
            response_text = agent.generate_response(prompt, history=history)

            # Successful return
            return ServiceResult(
                success=True,
                data=response_text,
                status_code=200
            )

        except ValueError as ve:
            # Handle specific known errors (e.g., missing environment variables)
            logger.warning(f"Validation error in PromptService: {str(ve)}")
            return ServiceResult(
                success=False,
                error_message=str(ve),
                status_code=400
            )
        except Exception as e:
            # Catch-all for SDK crashes, network failures, etc.
            logger.error(f"Critical error communicating with {provider.value}: {str(e)}", exc_info=True)
            return ServiceResult(
                success=False,
                error_message="An unexpected error occurred while communicating with the AI provider.",
                status_code=502  # Bad Gateway is accurate for upstream API failures
            )
