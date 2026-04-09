"""Speech-to-text service for audio uploads."""
from __future__ import annotations

import os
from io import BytesIO
from typing import Any

from app.core.config import get_settings


class SpeechToTextService:
    """Convert voice/audio bytes into text for downstream chatbot flow."""

    def __init__(self) -> None:
        self.settings = get_settings()

    @staticmethod
    def _pick_content_type(filename: str) -> str:
        ext = os.path.splitext(filename.lower())[1]
        if ext == ".wav":
            return "audio/wav"
        if ext in {".webm", ".weba"}:
            return "audio/webm"
        if ext == ".mp3":
            return "audio/mpeg"
        if ext == ".m4a":
            return "audio/mp4"
        if ext == ".ogg":
            return "audio/ogg"
        return "application/octet-stream"

    @staticmethod
    def _extract_text(result: Any) -> str:
        if hasattr(result, "text") and result.text:
            return str(result.text).strip()
        if isinstance(result, dict):
            return str(result.get("text", "")).strip()
        return ""

    def transcribe_audio_bytes(self, audio_bytes: bytes, filename: str | None = None) -> dict[str, Any]:
        """Transcribe audio bytes to text, preferring Groq Whisper when configured."""
        normalized_filename = filename or "voice.webm"
        audio_size_bytes = len(audio_bytes)

        if not audio_bytes:
            return {
                "status": "error",
                "text": "",
                "confidence": 0.0,
                "source": "none",
                "reason": "empty_audio",
                "audio_size_bytes": 0,
                "filename": normalized_filename,
            }

        if self.settings.GROQ_API_KEY:
            try:
                from groq import Groq

                client = Groq(api_key=self.settings.GROQ_API_KEY)
                model_candidates = ["whisper-large-v3-turbo", "whisper-large-v3"]
                content_type = self._pick_content_type(normalized_filename)

                last_error = None
                for model_name in model_candidates:
                    try:
                        # Prefer explicit multipart tuple format for compatibility.
                        result = client.audio.transcriptions.create(
                            file=(normalized_filename, audio_bytes, content_type),
                            model=model_name,
                            language="en",
                            response_format="verbose_json",
                            temperature=0,
                        )
                    except Exception:
                        # Fallback to file-like upload for SDK variants.
                        audio_file = BytesIO(audio_bytes)
                        audio_file.name = normalized_filename
                        result = client.audio.transcriptions.create(
                            file=audio_file,
                            model=model_name,
                            language="en",
                            response_format="verbose_json",
                            temperature=0,
                        )

                    text = self._extract_text(result)
                    if text:
                        return {
                            "status": "success",
                            "text": text,
                            "confidence": 0.9,
                            "source": "groq_whisper",
                            "model": model_name,
                            "audio_size_bytes": audio_size_bytes,
                            "filename": normalized_filename,
                        }
                    last_error = "empty_transcript"

                return {
                    "status": "fallback",
                    "text": "",
                    "confidence": 0.0,
                    "source": "groq_whisper",
                    "reason": str(last_error or "no_text_returned"),
                    "audio_size_bytes": audio_size_bytes,
                    "filename": normalized_filename,
                }
            except Exception as exc:
                return {
                    "status": "fallback",
                    "text": "",
                    "confidence": 0.0,
                    "source": "groq_whisper",
                    "reason": str(exc),
                    "audio_size_bytes": audio_size_bytes,
                    "filename": normalized_filename,
                }

        return {
            "status": "fallback",
            "text": "",
            "confidence": 0.0,
            "source": "unavailable",
            "reason": "transcription_service_not_configured",
            "audio_size_bytes": audio_size_bytes,
            "filename": normalized_filename,
        }
