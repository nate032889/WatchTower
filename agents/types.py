from enum import Enum
from dataclasses import dataclass
from typing import Optional

class LLMProvider(str, Enum):
    GEMINI = "gemini"
    CHATGPT = "chatgpt"
    CLAUDE = "claude"

@dataclass
class ServiceResult:
    """Standardized return type for all service layer operations."""
    success: bool
    data: Optional[str] = None
    error_message: Optional[str] = None
    status_code: int = 200
