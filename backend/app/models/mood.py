"""
Mood database model.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class MoodEntry(Base):
    """Model for storing user mood entries."""
    __tablename__ = "mood_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mood = Column(String, nullable=False)
    intensity = Column(Float, default=0.5)  # 0.0 to 1.0 scale
    notes = Column(String, nullable=True)
    detected_sentiment = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)
    stress_level = Column(String, nullable=True)  # "low", "moderate", "high"
    stress_score = Column(Float, nullable=True)  # 0-100 scale
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="mood_entries")
