"""
Detection routes - emotion/stress detection from text or media.
"""
from fastapi import APIRouter, Depends, UploadFile, File

router = APIRouter(prefix="/detect", tags=["Detection"])


@router.post("/text")
async def detect_from_text():
    """Detect emotional state from text input."""
    pass


@router.post("/media")
async def detect_from_media(file: UploadFile = File(...)):
    """Detect emotional state from uploaded media (image/audio)."""
    pass
