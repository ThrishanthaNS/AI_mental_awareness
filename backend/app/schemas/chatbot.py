"""
Pydantic schemas for Chatbot requests and responses.
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ChatMessageRequest(BaseModel):
    message: str
    session_id: Optional[int] = None


class ChatMessageResponse(BaseModel):
    response: str
    session_id: int
    detected_emotion: Optional[str] = None
    confidence: Optional[float] = None


class ChatHistory(BaseModel):
    session_id: int
    messages: List[dict]
    created_at: datetime
