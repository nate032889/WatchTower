from sqlalchemy.orm import Session, relationship
from sqlalchemy import Column, String, Text, Integer, ForeignKey
from pydantic import BaseModel, Field
from typing import List

from .database import Base, get_db

# --- Pydantic Models (DTOs) ---
class MessageDTO(BaseModel):
    role: str
    content: str

    class Config:
        from_attributes = True

class ConversationDTO(BaseModel):
    key: str
    messages: List[MessageDTO] = []

    class Config:
        from_attributes = True

# --- SQLAlchemy Models ---
class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    conversation = relationship("Conversation", back_populates="messages")

# --- Repository Class ---
class HistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_conversation(self, key: str) -> ConversationDTO:
        """
        Retrieves a full conversation with all its messages.
        :param key: The unique key for the conversation.
        :return: A ConversationDTO with the conversation's data.
        """
        conversation_db = self.db.query(Conversation).filter(Conversation.key == key).first()
        if not conversation_db:
            return ConversationDTO(key=key, messages=[])
        
        # Manually construct the DTO to ensure correct data shape
        messages_dto = [MessageDTO(role=msg.role, content=msg.content) for msg in conversation_db.messages]
        return ConversationDTO(key=conversation_db.key, messages=messages_dto)

    def add_message(self, key: str, role: str, content: str):
        """
        Adds a new message to a conversation.
        :param key: The key of the conversation to add the message to.
        :param role: The role of the message sender (e.g., 'user' or 'model').
        :param content: The text content of the message.
        :return: None
        """
        conversation_db = self.db.query(Conversation).filter(Conversation.key == key).first()
        if not conversation_db:
            conversation_db = Conversation(key=key)
            self.db.add(conversation_db)
        
        new_message = Message(role=role, content=content, conversation=conversation_db)
        self.db.add(new_message)
        self.db.commit()

    def replace_history(self, key: str, messages: List[MessageDTO]):
        """
        Replaces the entire history of a conversation, used for summarization.
        :param key: The key of the conversation to update.
        :param messages: A list of MessageDTOs representing the new history.
        :return: None
        """
        conversation_db = self.db.query(Conversation).filter(Conversation.key == key).first()
        if not conversation_db:
            conversation_db = Conversation(key=key)
            self.db.add(conversation_db)
        
        # Clear existing messages
        for msg in conversation_db.messages:
            self.db.delete(msg)
            
        # Add new messages
        for msg_dto in messages:
            new_message = Message(role=msg_dto.role, content=msg_dto.content, conversation=conversation_db)
            self.db.add(new_message)

        self.db.commit()

    @staticmethod
    def create_tables():
        """
        Creates all database tables defined in the Base metadata.
        :return: None
        """
        from .database import engine
        Base.metadata.create_all(bind=engine)
