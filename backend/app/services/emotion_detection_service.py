"""
Emotion detection service - detect emotions from text and media.
"""
from __future__ import annotations

from typing import Any


class EmotionDetectionService:
    """Service for detecting emotions from text, images, and audio/video."""

    POSITIVE_TERMS = {"good", "happy", "great", "calm", "better", "relaxed"}
    STRESS_TERMS = {"stress", "stressed", "anxious", "overwhelmed", "panic", "burnout"}

    def __init__(self):
        self.model = None

    def load_model(self):
        """Load the emotion detection model (placeholder for future model loading)."""
        return None

    @staticmethod
    def _risk_from_emotion(emotion: str, confidence: float) -> str:
        emotion_lower = emotion.lower().strip()
        if emotion_lower in {"fear", "sad", "angry", "stressed", "anxious", "overwhelmed"}:
            if confidence >= 0.75:
                return "high"
            return "medium"
        if emotion_lower in {"neutral", "surprised"}:
            return "medium" if confidence >= 0.8 else "low"
        return "low"

    @staticmethod
    def _response(
        status: str,
        emotion: str,
        confidence: float,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        normalized_confidence = max(0.0, min(1.0, float(confidence)))
        return {
            "status": status,
            "emotion": emotion,
            "confidence": round(normalized_confidence, 4),
            "risk_level": EmotionDetectionService._risk_from_emotion(emotion, normalized_confidence),
            "details": details or {},
        }

    def detect_from_text(self, text: str) -> dict[str, Any]:
        """
        Detect emotion from text input.
        Returns: {"status", "emotion", "confidence", "risk_level", "details"}
        """
        normalized = (text or "").lower()
        if any(term in normalized for term in self.STRESS_TERMS):
            return self._response("success", "stressed", 0.84, {"source": "keyword_text"})
        if any(term in normalized for term in self.POSITIVE_TERMS):
            return self._response("success", "happy", 0.79, {"source": "keyword_text"})
        return self._response("success", "neutral", 0.62, {"source": "keyword_text"})

    def detect_from_image(self, image_path: str) -> dict[str, Any]:
        """Detect emotion from facial expression in an image path."""
        return self._response("fallback", "neutral", 0.55, {"source": "image_path", "path": image_path})

    def detect_from_audio(self, audio_path: str) -> dict[str, Any]:
        """Detect emotion from voice/audio input."""
        return self._response("fallback", "neutral", 0.55, {"source": "audio_path", "path": audio_path})

    def detect_from_video_bytes(self, video_bytes: bytes, filename: str | None = None) -> dict[str, Any]:
        """Detect facial emotion from uploaded video/image bytes using OpenCV when available."""
        if not video_bytes:
            return self._response("error", "unknown", 0.0, {"reason": "empty_media"})

        try:
            import cv2  # type: ignore
            import numpy as np  # type: ignore
        except Exception:
            # Graceful fallback when optional video stack is unavailable.
            return self._response(
                "fallback",
                "neutral",
                0.56,
                {
                    "reason": "opencv_unavailable",
                    "source": filename or "video_upload",
                },
            )

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        frame = None

        # Try direct decode first (works when frontend sends a captured image frame as video payload).
        arr = np.frombuffer(video_bytes, dtype=np.uint8)
        decoded = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if decoded is not None:
            frame = decoded
        else:
            # Attempt reading as an actual video stream.
            temp_name = filename or "temp_video.bin"
            try:
                import tempfile
                from pathlib import Path

                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(temp_name).suffix or ".webm") as tmp:
                    tmp.write(video_bytes)
                    temp_path = tmp.name

                cap = cv2.VideoCapture(temp_path)
                ok, first_frame = cap.read()
                cap.release()
                frame = first_frame if ok else None

                Path(temp_path).unlink(missing_ok=True)
            except Exception:
                frame = None

        if frame is None:
            return self._response(
                "fallback",
                "neutral",
                0.52,
                {"reason": "decode_failed", "source": filename or "video_upload"},
            )

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60))

        if len(faces) == 0:
            return self._response(
                "success",
                "neutral",
                0.6,
                {"faces_detected": 0, "source": filename or "video_upload"},
            )

        # Heuristic expression scoring based on brightness/variance in largest detected face.
        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        face_roi = gray[y : y + h, x : x + w]
        mean_intensity = float(face_roi.mean())
        variance = float(face_roi.var())

        if mean_intensity > 145 and variance > 900:
            emotion = "happy"
            confidence = 0.78
        elif mean_intensity < 95 and variance > 850:
            emotion = "sad"
            confidence = 0.76
        elif variance > 1300:
            emotion = "anxious"
            confidence = 0.74
        else:
            emotion = "neutral"
            confidence = 0.68

        return self._response(
            "success",
            emotion,
            confidence,
            {
                "faces_detected": int(len(faces)),
                "source": filename or "video_upload",
            },
        )
