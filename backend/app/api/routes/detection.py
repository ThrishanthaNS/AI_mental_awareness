"""
Detection routes - emotion/stress detection from text or media.
"""
from __future__ import annotations

from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

from app.services.emotion_detection_service import EmotionDetectionService

router = APIRouter(prefix="/detect", tags=["Detection"])
emotion_service = EmotionDetectionService()


class DetectTextRequest(BaseModel):
    text: str


@router.post("/text")
async def detect_from_text(payload: DetectTextRequest):
    """Detect emotional state from text input."""
    return emotion_service.detect_from_text(payload.text)


@router.post("/media")
async def detect_from_media(file: UploadFile = File(...)):
    """Detect emotional state from uploaded media (image/video)."""
    content = await file.read()
    result = emotion_service.detect_from_video_bytes(content, filename=file.filename)
    result["source"] = file.filename
    return result
