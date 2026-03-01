import os
import requests
import logging
from typing import List, Tuple
from data.history_repository import HistoryRepository, MessageDTO, EvidenceDTO

# --- Configuration ---
HISTORY_THRESHOLD = 20
API_ENDPOINT = os.getenv('WATCHTOWER_API_ENDPOINT')

logger = logging.getLogger(__name__)

class ConversationService:
    def __init__(self, repo: HistoryRepository):
        self.repo = repo

    def _summarize_conversation(self, conversation: List[MessageDTO]) -> List[MessageDTO]:
        """
        Calls the LLM to summarize a long conversation history.
        :param conversation: The list of MessageDTOs to summarize.
        :return: A new, condensed list of MessageDTOs.
        """
        logger.info(f"History length {len(conversation)} exceeds threshold {HISTORY_THRESHOLD}. Summarizing...")
        
        history_text = "\\n".join([f"{msg.role}: {msg.content}" for msg in conversation])
        summary_prompt = (
            "The following is a conversation history. Please summarize it concisely, "
            "retaining all key facts, names, and topics. The summary will be used as the "
            "starting context for a future conversation."
            f"\\n\\n--- CONVERSATION HISTORY ---\\n{history_text}"
        )
        
        try:
            response = requests.post(API_ENDPOINT, json={'prompt': summary_prompt, 'history': []})
            response.raise_for_status()
            summary_text = response.json().get('response', '')

            if not summary_text:
                logger.warning("Summarization failed. Falling back to sliding window.")
                return conversation[-HISTORY_THRESHOLD:]

            new_history = [
                MessageDTO(role='user', content=f"Summary of the conversation so far: {summary_text}"),
                MessageDTO(role='model', content="Understood. I have absorbed the context and am ready to continue.")
            ]
            logger.info("Summarization successful. New history created.")
            return new_history

        except requests.exceptions.RequestException as e:
            logger.error(f"Error during summarization API call: {e}. Falling back to sliding window.")
            return conversation[-HISTORY_THRESHOLD:]

    def get_history_for_message(self, channel_id: int, user_id: int, is_thread: bool) -> Tuple[str, List[MessageDTO]]:
        """
        Determines the correct history key and retrieves the conversation.
        :param channel_id: The ID of the channel (or parent channel for threads).
        :param user_id: The ID of the user who sent the message.
        :param is_thread: A boolean indicating if the message is in a thread.
        :return: A tuple containing the history key and the list of messages.
        """
        if is_thread:
            history_key = f"thread_{channel_id}_{user_id}"
            conversation = self.repo.get_conversation(history_key)
            if not conversation.messages:
                parent_key = f"channel_{channel_id}"
                conversation = self.repo.get_conversation(parent_key)
                logger.info(f"Inheriting global context from channel {channel_id} for user {user_id}")
        else:
            history_key = f"channel_{channel_id}"
            conversation = self.repo.get_conversation(history_key)
        
        return history_key, conversation.messages

    def add_turn_to_history(self, key: str, user_prompt: str, model_response: str):
        """
        Adds a user prompt and a model response to the history.
        :param key: The key for the conversation.
        :param user_prompt: The text of the user's message.
        :param model_response: The text of the model's response.
        """
        self.repo.add_message(key, role='user', content=user_prompt)
        self.repo.add_message(key, role='model', content=model_response)

    def check_and_summarize(self, key: str):
        """
        Checks if a conversation is too long and summarizes it if needed.
        :param key: The key for the conversation to check.
        """
        conversation = self.repo.get_conversation(key)
        if len(conversation.messages) > HISTORY_THRESHOLD:
            new_history = self._summarize_conversation(conversation.messages)
            self.repo.replace_history(key, new_history)

    # --- Operational Memory Commands ---

    def create_occurrence_and_bind_channel(self, label: str, workflow: str, channel_id: int) -> str:
        """
        Creates a new occurrence and binds the current channel to it.
        :param label: The label for the occurrence.
        :param workflow: The workflow type (e.g., 'pentest').
        :param channel_id: The ID of the Discord channel.
        :return: A status message.
        """
        try:
            occurrence = self.repo.create_occurrence(label=label, workflow=workflow)
            binding_key = f"channel_{channel_id}"
            self.repo.set_binding(binding_key, occurrence.id)
            return f"✅ Occurrence '{label}' created (ID: {occurrence.id}) and bound to this channel."
        except Exception as e:
            logger.error(f"Failed to create occurrence: {e}")
            return f"❌ Failed to create occurrence: {str(e)}"

    def submit_evidence(self, content: str, channel_id: int, user_id: int) -> str:
        """
        Submits evidence to the active occurrence for the channel.
        :param content: The evidence content.
        :param channel_id: The ID of the Discord channel.
        :param user_id: The ID of the user submitting the evidence.
        :return: A status message.
        """
        binding_key = f"channel_{channel_id}"
        occurrence_id = self.repo.get_binding(binding_key)
        
        if not occurrence_id:
            return "❌ No active occurrence bound to this channel. Use `!wt set_occurrence` first."

        try:
            evidence = self.repo.add_evidence(occurrence_id, content, source=f"user_{user_id}")
            return f"✅ Evidence submitted (ID: {evidence.id})."
        except Exception as e:
            logger.error(f"Failed to submit evidence: {e}")
            return f"❌ Failed to submit evidence: {str(e)}"

    def generate_closeout_summary(self, channel_id: int) -> str:
        """
        Generates a closeout summary based on all evidence for the active occurrence.
        :param channel_id: The ID of the Discord channel.
        :return: The generated summary or an error message.
        """
        binding_key = f"channel_{channel_id}"
        occurrence_id = self.repo.get_binding(binding_key)
        
        if not occurrence_id:
            return "❌ No active occurrence bound to this channel. Use `!wt set_occurrence` first."

        evidence_list = self.repo.get_evidence_for_occurrence(occurrence_id)
        if not evidence_list:
            return "⚠️ No evidence found for this occurrence. Submit evidence using `!wt submit_evidence`."

        evidence_text = "\\n".join([f"- {e.content} (Source: {e.source})" for e in evidence_list])
        prompt = (
            f"Please generate a formal closeout summary for the following operational occurrence.\\n"
            f"Review all the collected evidence below and synthesize a report.\\n\\n"
            f"--- COLLECTED EVIDENCE ---\\n{evidence_text}"
        )

        try:
            # We send this as a fresh request without history to get a clean summary
            # Note: We are bypassing the usual history mechanism here for a focused task
            response = requests.post(API_ENDPOINT, json={'prompt': prompt, 'history': []})
            response.raise_for_status()
            return response.json().get('response', '❌ Failed to generate summary.')
        except Exception as e:
            logger.error(f"Failed to generate closeout: {e}")
            return f"❌ Error generating closeout: {str(e)}"
