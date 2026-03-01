import json
from datetime import datetime
from sqlalchemy.orm import Session, relationship
from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, Boolean, JSON
from pydantic import BaseModel
from typing import List, Optional, Any

from .database import Base

# --- Pydantic Models (DTOs) ---
class OccurrenceDTO(BaseModel):
    id: int
    label: str
    domain: str
    workflow: str
    created_at: datetime
    status: str

    class Config:
        from_attributes = True

class EvidenceDTO(BaseModel):
    id: int
    occurrence_id: int
    content: str
    source: str
    is_quarantined: bool

    class Config:
        from_attributes = True

class ActiveKnowledgeDTO(BaseModel):
    id: int
    domain: str
    content: str
    references: List[int]

    class Config:
        from_attributes = True

class MessageDTO(BaseModel):
    id: int
    role: str
    content: str
    occurrence_id: Optional[int] = None

    class Config:
        from_attributes = True

class ConversationDTO(BaseModel):
    key: str
    messages: List[MessageDTO] = []

    class Config:
        from_attributes = True

# --- SQLAlchemy Models ---
class Occurrence(Base):
    __tablename__ = "occurrences"
    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, nullable=False, unique=True)
    domain = Column(String, default='security')
    workflow = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default='active')
    
    evidences = relationship("Evidence", back_populates="occurrence", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="occurrence")

class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(Integer, primary_key=True, index=True)
    occurrence_id = Column(Integer, ForeignKey("occurrences.id"))
    content = Column(Text, nullable=False)
    source = Column(String)
    is_quarantined = Column(Boolean, default=False)
    
    occurrence = relationship("Occurrence", back_populates="evidences")

class ActiveKnowledge(Base):
    __tablename__ = "active_knowledge"
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    references = Column(JSON, default=[]) # List of Evidence IDs

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
    occurrence_id = Column(Integer, ForeignKey("occurrences.id"), nullable=True)
    
    conversation = relationship("Conversation", back_populates="messages")
    occurrence = relationship("Occurrence", back_populates="messages")

class ConversationBinding(Base):
    __tablename__ = "conversation_bindings"
    conversation_key = Column(String, primary_key=True, index=True)
    occurrence_id = Column(Integer, ForeignKey("occurrences.id"))
    
    occurrence = relationship("Occurrence")

# --- Repository Class ---
class HistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_conversation(self, key: str) -> ConversationDTO:
        """Retrieves a full conversation with all its messages."""
        conversation_db = self.db.query(Conversation).filter(Conversation.key == key).first()
        if not conversation_db:
            return ConversationDTO(key=key, messages=[])
        
        messages_dto = [MessageDTO.model_validate(msg) for msg in conversation_db.messages]
        return ConversationDTO(key=conversation_db.key, messages=messages_dto)

    def add_message(self, key: str, role: str, content: str, occurrence_id: Optional[int] = None):
        """Adds a new message to a conversation."""
        conversation_db = self.db.query(Conversation).filter(Conversation.key == key).first()
        if not conversation_db:
            conversation_db = Conversation(key=key)
            self.db.add(conversation_db)
        
        new_message = Message(role=role, content=content, conversation=conversation_db, occurrence_id=occurrence_id)
        self.db.add(new_message)
        self.db.commit()

    def replace_history(self, key: str, messages: List[MessageDTO]):
        """Replaces the entire history of a conversation (used for summarization)."""
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

    # --- Operational Memory Methods ---

    def create_occurrence(self, label: str, workflow: str, domain: str = 'security') -> OccurrenceDTO:
        """Creates a new occurrence."""
        new_occurrence = Occurrence(label=label, workflow=workflow, domain=domain)
        self.db.add(new_occurrence)
        self.db.commit()
        self.db.refresh(new_occurrence)
        return OccurrenceDTO.model_validate(new_occurrence)

    def get_binding(self, conversation_key: str) -> Optional[int]:
        """Gets the active occurrence ID for a conversation key."""
        binding = self.db.query(ConversationBinding).filter(ConversationBinding.conversation_key == conversation_key).first()
        return binding.occurrence_id if binding else None

    def set_binding(self, conversation_key: str, occurrence_id: int):
        """Binds a conversation key to an occurrence ID."""
        binding = self.db.query(ConversationBinding).filter(ConversationBinding.conversation_key == conversation_key).first()
        if binding:
            binding.occurrence_id = occurrence_id
        else:
            binding = ConversationBinding(conversation_key=conversation_key, occurrence_id=occurrence_id)
            self.db.add(binding)
        self.db.commit()

    def add_evidence(self, occurrence_id: int, content: str, source: str) -> EvidenceDTO:
        """Adds evidence to an occurrence."""
        new_evidence = Evidence(occurrence_id=occurrence_id, content=content, source=source)
        self.db.add(new_evidence)
        self.db.commit()
        self.db.refresh(new_evidence)
        return EvidenceDTO.model_validate(new_evidence)

    def get_evidence_for_occurrence(self, occurrence_id: int) -> List[EvidenceDTO]:
        """Retrieves all evidence for a given occurrence."""
        evidence_db = self.db.query(Evidence).filter(Evidence.occurrence_id == occurrence_id).all()
        return [EvidenceDTO.model_validate(e) for e in evidence_db]

    @staticmethod
    def create_tables():
        """Creates all database tables."""
        from .database import engine
        Base.metadata.create_all(bind=engine)
