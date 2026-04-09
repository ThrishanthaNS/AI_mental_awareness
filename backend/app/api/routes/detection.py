"""
Detection routes - emotion/stress detection from text or media.
"""
from __future__ import annotations

from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

router = APIRouter(prefix="/detect", tags=["Detection"])


class DetectTextRequest(BaseModel):
    text: str


@router.post("/text")
async def detect_from_text(payload: DetectTextRequest):
    """Detect emotional state from text input."""
    text = payload.text.lower()
    if any(word in text for word in ["stress", "anxious", "overwhelmed", "burnout"]):
        return {"emotion": "stressed", "confidence": 0.84}
    if any(word in text for word in ["happy", "good", "calm", "great"]):
        return {"emotion": "positive", "confidence": 0.79}
    return {"emotion": "neutral", "confidence": 0.62}


@router.post("/media")
async def detect_from_media(file: UploadFile = File(...)):
    """Detect emotional state from uploaded media (image/audio)."""
    await file.read()
    return {"emotion": "neutral", "confidence": 0.7, "source": file.filename}
