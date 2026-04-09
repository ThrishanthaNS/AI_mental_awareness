"""
Pydantic schemas for Chatbot requests and responses.
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ChatMessageRequest(BaseModel):
    message: str
    session_id: Optional[int] = None
    age: Optional[int] = None
    profession: Optional[str] = None
    typing_speed: Optional[float] = None
    screen_time: Optional[float] = None
    sentiment: Optional[str] = None
    emotion: Optional[str] = None
    history_stress: Optional[List[float]] = None
    history_emotions: Optional[List[str]] = None
    trend_description: Optional[str] = None


class StructuredChatOutput(BaseModel):
    stress_level: Optional[str] = None
    emotion: Optional[str] = None
    reason: Optional[str] = None
    response: Optional[str] = None
    action: Optional[str] = None


class ChatMessageResponse(BaseModel):
    response: str
    session_id: int
    detected_emotion: Optional[str] = None
    confidence: Optional[float] = None
    structured: Optional[StructuredChatOutput] = None


class ChatHistory(BaseModel):
    session_id: int
    messages: List[dict]
    created_at: datetime
