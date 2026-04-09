"""
Mood tracking routes - log mood, get history, analytics.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.models.mood import MoodEntry

router = APIRouter(prefix="/mood", tags=["Mood Tracking"])


class MoodLogRequest(BaseModel):
    user_id: int = 1
    mood: str
    intensity: float = 0.5
    notes: str | None = None
    stress_level: str | None = None
    stress_score: float | None = None


class MoodEntryResponse(BaseModel):
    id: int
    user_id: int
    mood: str
    intensity: float
    notes: str | None = None
    detected_sentiment: str | None = None
    confidence_score: float | None = None
    stress_level: str | None = None
    stress_score: float | None = None
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/log")
async def log_mood(
    payload: MoodLogRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Log a new mood entry."""
    entry = MoodEntry(
        user_id=payload.user_id,
        mood=payload.mood,
        intensity=max(0.0, min(1.0, payload.intensity)),
        notes=payload.notes,
        stress_level=payload.stress_level,
        stress_score=payload.stress_score,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    
    return {
        "id": entry.id,
        "user_id": entry.user_id,
        "mood": entry.mood,
        "intensity": entry.intensity,
        "notes": entry.notes,
        "stress_level": entry.stress_level,
        "stress_score": entry.stress_score,
        "created_at": entry.created_at.isoformat(),
    }


@router.get("/history")
async def get_mood_history(
    user_id: int = 1,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Get mood history for a user."""
    entries = db.query(MoodEntry).filter(
        MoodEntry.user_id == user_id
    ).order_by(desc(MoodEntry.created_at)).limit(limit).all()
    
    return {
        "user_id": user_id,
        "entries": [
            {
                "id": e.id,
                "mood": e.mood,
                "intensity": e.intensity,
                "notes": e.notes,
                "stress_level": e.stress_level,
                "stress_score": e.stress_score,
                "created_at": e.created_at.isoformat(),
            }
            for e in entries
        ],
    }


@router.get("/analytics")
async def get_mood_analytics(
    user_id: int = 1,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Get mood analytics and trends for a user."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    entries = db.query(MoodEntry).filter(
        MoodEntry.user_id == user_id,
        MoodEntry.created_at >= cutoff_date,
    ).all()
    
    if not entries:
        return {
            "user_id": user_id,
            "total_entries": 0,
            "period_days": days,
            "most_frequent_mood": None,
            "average_intensity": 0.0,
            "average_stress_score": 0.0,
            "mood_distribution": {},
            "stress_levels_distribution": {},
        }

    mood_counter = Counter(entry.mood for entry in entries)
    stress_counter = Counter(entry.stress_level for entry in entries if entry.stress_level)
    
    average_intensity = sum(entry.intensity for entry in entries) / len(entries)
    stress_scores = [e.stress_score for e in entries if e.stress_score is not None]
    average_stress_score = sum(stress_scores) / len(stress_scores) if stress_scores else 0.0

    return {
        "user_id": user_id,
        "total_entries": len(entries),
        "period_days": days,
        "most_frequent_mood": mood_counter.most_common(1)[0][0] if mood_counter else None,
        "average_intensity": round(average_intensity, 3),
        "average_stress_score": round(average_stress_score, 2),
        "mood_distribution": dict(mood_counter),
        "stress_levels_distribution": dict(stress_counter),
    }


@router.get("/trends")
async def get_mood_trends(
    user_id: int = 1,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Get mood trend data for time series visualization."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    entries = db.query(MoodEntry).filter(
        MoodEntry.user_id == user_id,
        MoodEntry.created_at >= cutoff_date,
    ).order_by(MoodEntry.created_at).all()
    
    # Group entries by day
    daily_data = {}
    for entry in entries:
        day_key = entry.created_at.date().isoformat()
        if day_key not in daily_data:
            daily_data[day_key] = {
                "entries": [],
                "avg_intensity": 0.0,
                "avg_stress": 0.0,
            }
        daily_data[day_key]["entries"].append({
            "mood": entry.mood,
            "intensity": entry.intensity,
            "stress_score": entry.stress_score,
            "stress_level": entry.stress_level,
        })
    
    # Calculate daily averages
    for day_key in daily_data:
        day_entries = daily_data[day_key]["entries"]
        daily_data[day_key]["avg_intensity"] = round(
            sum(e["intensity"] for e in day_entries) / len(day_entries), 2
        )
        stress_scores = [e["stress_score"] for e in day_entries if e["stress_score"] is not None]
        daily_data[day_key]["avg_stress"] = round(
            sum(stress_scores) / len(stress_scores), 2
        ) if stress_scores else 0.0
    
    return {
        "user_id": user_id,
        "period_days": days,
        "daily_data": daily_data,
    }
