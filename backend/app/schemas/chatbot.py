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
    message_id: Optional[int] = None
    detected_emotion: Optional[str] = None
    confidence: Optional[float] = None
    stress_score: Optional[float] = None
    stress_level: Optional[str] = None
    structured: Optional[StructuredChatOutput] = None


class ChatMessageDB(BaseModel):
    """Schema for storing individual chat message in database."""
    role: str
    content: str
    detected_emotion: Optional[str] = None
    confidence: Optional[float] = None
    stress_score: Optional[float] = None
    stress_level: Optional[str] = None
    created_at: Optional[datetime] = None


class ChatMessageDetailedDB(ChatMessageDB):
    """Extended schema with database-generated fields."""
    id: int
    session_id: int
    
    class Config:
        from_attributes = True


class ChatHistory(BaseModel):
    session_id: int
    messages: List[ChatMessageDetailedDB]
    created_at: datetime


class ChatSessionDB(BaseModel):
    """Schema for chat session."""
    id: int
    user_id: int
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


class ChatSessionCreateRequest(BaseModel):
    """Request to create a new chat session."""
    user_id: int
    title: Optional[str] = None
