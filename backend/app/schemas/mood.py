"""
Pydantic schemas for Mood requests and responses.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MoodCreate(BaseModel):
    mood: str
    intensity: float = 0.5
    notes: Optional[str] = None


class MoodResponse(BaseModel):
    id: int
    mood: str
    intensity: float
    notes: Optional[str]
    detected_sentiment: Optional[str]
    confidence_score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class MoodAnalytics(BaseModel):
    total_entries: int
    most_frequent_mood: str
    average_intensity: float
    mood_distribution: dict
