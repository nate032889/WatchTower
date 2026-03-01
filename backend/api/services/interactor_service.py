import logging
from typing import Tuple, Dict, Any, Optional

from agents.agent import get_llm_agent
from agents.types import LLMProvider
from api.infrastructure.intake_client import IntakeServiceClient
from api.models import Conversation, Message, Evidence, ProviderCredential, Organization

logger = logging.getLogger(__name__)


class InteractorService:
    """
    Handles the core business logic for processing messages from stateless interactors.
    """

    @staticmethod
    def _get_or_create_conversation(payload: Dict[str, Any]) -> Conversation:
        """
        Finds or creates a Conversation record based on the incoming platform and channel ID.
        """
        platform_channel_id = f"{payload['platform']}_{payload['channel_id']}"
        conversation, created = Conversation.objects.get_or_create(
            platform_channel_id=platform_channel_id
        )
        if created:
            logger.info(f"Created new conversation for channel: {conversation.platform_channel_id}")
        return conversation

    @staticmethod
    def _process_attachments(
        payload: Dict[str, Any], conversation: Conversation
    ) -> Tuple[str, Optional[Exception]]:
        """
        Processes attachments and returns enriched context. Returns an error if no occurrence is active.
        """
        attachment_urls = payload.get("attachment_urls", [])
        if not attachment_urls:
            return "", None

        if not conversation.occurrence:
            logger.warning(f"Conversation {conversation.id} has no active occurrence. Cannot process attachments.")
            return "", ValueError("Attachments were sent, but no active occurrence is bound to this conversation.")

        enriched_context = ""
        for url in attachment_urls:
            intake_data, err = IntakeServiceClient.process_attachment(url)
            if err:
                logger.error(f"Failed to process attachment {url}: {err}")
                enriched_context += f"--- Error processing attachment: {url} ---\\n"
                continue

            object_key = intake_data.get("object_key")
            extracted_text = intake_data.get("extracted_text")
            Evidence.objects.create(
                occurrence=conversation.occurrence,
                content=extracted_text,
                source_type="attachment",
                object_reference=object_key,
            )

            filename = url.split('/')[-1]
            enriched_context += f"--- Content of attached file: {filename} ---\\n{extracted_text}\\n--- End of file ---\\n\\n"

        return enriched_context, None

    @staticmethod
    def _get_llm_credentials(organization_id: int) -> Tuple[LLMProvider, str]:
        """
        Retrieves the active LLM credentials for the given organization.
        Defaults to Gemini if multiple are found, or raises an error if none exist.
        """
        try:
            # Try to find a Gemini credential first as the default
            cred = ProviderCredential.objects.filter(
                organization_id=organization_id, 
                is_active=True, 
                provider='gemini'
            ).first()
            
            # If no Gemini, take any active credential
            if not cred:
                cred = ProviderCredential.objects.filter(
                    organization_id=organization_id, 
                    is_active=True
                ).first()

            if not cred:
                raise ValueError(f"No active LLM provider credentials found for organization {organization_id}")

            return LLMProvider(cred.provider), cred.api_key

        except Exception as e:
            logger.error(f"Error fetching credentials: {e}")
            raise

    @staticmethod
    def process_incoming_message(payload: Dict[str, Any]) -> Tuple[Optional[str], Optional[Exception]]:
        """
        Orchestrates the entire process of handling an incoming message.
        """
        try:
            # 1. Get Conversation context
            conversation = InteractorService._get_or_create_conversation(payload)

            # 2. Process attachments
            attachment_context, err = InteractorService._process_attachments(payload, conversation)
            if err:
                return None, err

            # 3. Save user message
            final_content = attachment_context + payload["content"]
            user_message = Message.objects.create(conversation=conversation, role="user", content=final_content)

            # 4. Get LLM Credentials for the Organization
            organization_id = payload.get("organization_id")
            if not organization_id:
                 return None, ValueError("Organization ID is missing from the payload.")
            
            provider, api_key = InteractorService._get_llm_credentials(organization_id)

            # 5. Call LLM
            # Efficiently fetch history by excluding the message we just created
            history = conversation.messages.exclude(id=user_message.id).order_by("created_at")
            
            agent = get_llm_agent(provider, api_key=api_key)

            response_text = agent.generate_response(
                prompt=final_content, history=list(history)
            )

            # 6. Save response
            Message.objects.create(conversation=conversation, role="model", content=response_text)

            return response_text, None

        except Exception as e:
            logger.error(f"Critical error in InteractorService: {e}", exc_info=True)
            return None, e
