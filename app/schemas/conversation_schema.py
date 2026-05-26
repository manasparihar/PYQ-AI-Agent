from pydantic import BaseModel, Field
from typing import List

class Message(BaseModel):
    """
    Schema for a single message in the conversation.
    """
    role: str = Field(..., max_length=15)
    content: str = Field(..., max_length=15000)
    timestamp: str = Field(..., max_length=30)

class ConversationSession(BaseModel):
    """
    Schema for an entire conversation session.
    """
    session_id: str = Field(..., max_length=50)
    messages: List[Message]

class ChatRequest(BaseModel):
    """
    Schema for the incoming request to the /chat endpoint.
    Strictly validated to prevent oversized prompt injection or memory exhaustion.
    """
    prompt: str = Field(..., min_length=1, max_length=2000, description="The user's input prompt. Limited to 2000 chars.")
