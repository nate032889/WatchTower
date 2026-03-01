import logging
from typing import Tuple, Dict, Any, Optional, List

from agents.agent import get_llm_agent
from agents.types import LLMProvider
from api.infrastructure.intake_client import IntakeServiceClient
from api.models import Conversation, Message, Evidence

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
        enriched_context = ""
        if not conversation.occurrence:
            logger.warning(f"Conversation {conversation.id} has no active occurrence. Cannot process attachments.")
            return "", ValueError("No active occurrence is bound to this conversation to associate evidence with.")

        for url in payload.get("attachment_urls", []):
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
    def process_incoming_message(payload: Dict[str, Any]) -> Tuple[Optional[str], Optional[Exception]]:
        """
        Orchestrates the entire process of handling an incoming message.
        """
        # 1. Get Conversation and Occurrence context
        conversation = InteractorService._get_or_create_conversation(payload)

        # 2. Process attachments to enrich the prompt
        attachment_context, err = InteractorService._process_attachments(payload, conversation)
        if err:
            return None, err

        # 3. Save the user's message
        final_content = attachment_context + payload["content"]
        Message.objects.create(conversation=conversation, role="user", content=final_content)

        # 4. Retrieve history and call the LLM
        messages = conversation.messages.order_by("created_at").all()
        
        try:
            agent = get_llm_agent(LLMProvider.GEMINI)
            # Pass the raw Django queryset directly to the agent
            response_text = agent.generate_response(
                prompt=final_content, history=messages[:-1] # Pass all but the last message
            )
        except Exception as e:
            logger.error(f"LLM generation failed for conversation {conversation.id}: {e}", exc_info=True)
            return None, e

        # 5. Save the model's response
        Message.objects.create(conversation=conversation, role="model", content=response_text)

        # 6. Return the result
        return response_text, None
