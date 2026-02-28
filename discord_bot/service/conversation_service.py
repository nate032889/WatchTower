import os
import requests
import logging
from typing import List, Tuple
from ..data.history_repository import HistoryRepository, MessageDTO

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
