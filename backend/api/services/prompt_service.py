import logging
import re
import requests
from agents.agent import get_llm_agent
from agents.types import LLMProvider, ServiceResult
from api.serializers.prompt import PromptSerializer
from .intake_validation_service import IntakeValidationService

logger = logging.getLogger(__name__)

# --- Microservice Integration ---

class RetrievalClient:
    """
    A client to communicate with the internal Go-based retrieval microservice.
    """
    BASE_URL = "http://go-retrieval-service:3000/api/v1/evidence/"
    FILE_REFERENCE_REGEX = re.compile(r"\[file:([\w.-]+)\]")

    @classmethod
    def fetch_evidence(cls, object_key: str) -> tuple[bool, str]:
        """
        Fetches and returns the pre-parsed text from the retrieval service.
        :param object_key: The key of the object to retrieve from Minio.
        :return: A tuple of (success, content/error_message).
        """
        try:
            url = f"{cls.BASE_URL}{object_key}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return True, data.get("llm_ready_text", "")
        except requests.exceptions.RequestException as e:
            logger.error(f"Retrieval service call failed for key '{object_key}': {e}")
            return False, f"Error retrieving file '{object_key}': Could not connect to retrieval service."

    @classmethod
    def enrich_prompt_with_evidence(cls, prompt: str) -> str:
        """
        Parses a prompt for file references, fetches them, and prepends them to the prompt.
        :param prompt: The user's original prompt.
        :return: The enriched prompt with file content.
        """
        matches = cls.FILE_REFERENCE_REGEX.finditer(prompt)
        enriched_content = ""
        
        for match in matches:
            object_key = match.group(1)
            success, content = cls.fetch_evidence(object_key)
            enriched_content += f"--- Content of file: {object_key} ---\\n{content}\\n--- End of file: {object_key} ---\\n\\n"
        
        # Remove the file references from the original prompt to avoid confusion
        clean_prompt = cls.FILE_REFERENCE_REGEX.sub("", prompt).strip()
        
        return enriched_content + clean_prompt

class PromptService:
    @staticmethod
    def process_prompt_request(request_data) -> ServiceResult:
        """
        Handles the entire process of validating a prompt request,
        executing it, and returning a ServiceResult.
        """
        # 1. Schema Validation
        serializer = PromptSerializer(data=request_data)
        if not serializer.is_valid():
            return ServiceResult(success=False, error_message=str(serializer.errors), status_code=400)

        validated_data = serializer.validated_data
        
        # 2. Vocabulary & Business Rule Validation
        validation_result = IntakeValidationService.validate_vocabulary(validated_data['metadata'])
        if not validation_result.success:
            return validation_result

        # --- Validation Passed ---
        content = validated_data['content']
        provider = LLMProvider(validated_data['provider'])
        history = validated_data.get('history', [])

        # 3. Evidence Retrieval and Enrichment
        try:
            enriched_content = RetrievalClient.enrich_prompt_with_evidence(content)
        except Exception as e:
            # This catches errors during the enrichment process itself
            logger.critical(f"Failed during evidence enrichment: {e}")
            return ServiceResult(success=False, error_message="Failed to process file references.", status_code=500)

        # 4. LLM Generation
        try:
            agent = get_llm_agent(provider)
            response_text = agent.generate_response(enriched_content, history=history)
            return ServiceResult(success=True, data=response_text, status_code=200)
        except Exception as e:
            logger.error(f"Critical error communicating with {provider.value}: {str(e)}", exc_info=True)
            return ServiceResult(success=False, error_message="An unexpected error occurred with the AI provider.", status_code=502)
