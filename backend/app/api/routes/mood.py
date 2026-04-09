"""
Mood tracking routes - log mood, get history, analytics.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/mood", tags=["Mood Tracking"])


class MoodLogRequest(BaseModel):
    mood: str
    intensity: float = 0.5
    notes: str | None = None


_mood_entries: list[dict] = []


@router.post("/log")
async def log_mood(payload: MoodLogRequest) -> dict:
    """Log a new mood entry."""
    entry = {
        "id": len(_mood_entries) + 1,
        "mood": payload.mood,
        "intensity": max(0.0, min(1.0, payload.intensity)),
        "notes": payload.notes,
        "created_at": datetime.utcnow().isoformat(),
    }
    _mood_entries.append(entry)
    return entry


@router.get("/history")
async def get_mood_history():
    """Get mood history for the authenticated user."""
    return {"entries": _mood_entries}


@router.get("/analytics")
async def get_mood_analytics():
    """Get mood analytics and trends."""
    if not _mood_entries:
        return {
            "total_entries": 0,
            "most_frequent_mood": "none",
            "average_intensity": 0.0,
            "mood_distribution": {},
        }

    mood_counter = Counter(entry["mood"] for entry in _mood_entries)
    average_intensity = sum(entry["intensity"] for entry in _mood_entries) / len(_mood_entries)

    return {
        "total_entries": len(_mood_entries),
        "most_frequent_mood": mood_counter.most_common(1)[0][0],
        "average_intensity": round(average_intensity, 3),
        "mood_distribution": dict(mood_counter),
    }
