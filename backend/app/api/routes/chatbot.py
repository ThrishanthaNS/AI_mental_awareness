"""
Chatbot routes - conversational mental health support.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, File, Form, Request, UploadFile, Depends
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.session import ChatMessage, ChatSession
from app.services.emotion_detection_service import EmotionDetectionService
from app.services.chatbot_service import ChatbotService
from app.services.speech_to_text_service import SpeechToTextService

router = APIRouter(prefix="/chat", tags=["Chatbot"])

_chatbot_service = ChatbotService()
_emotion_detection_service = EmotionDetectionService()
_speech_to_text_service = SpeechToTextService()


def _create_session(db: Session) -> int:
    session = ChatSession()
    db.add(session)
    db.commit()
    db.refresh(session)
    return int(session.id)


def _session_exists(db: Session, session_id: int) -> bool:
    return db.query(ChatSession.id).filter(ChatSession.id == session_id).first() is not None


def _add_message(db: Session, session_id: int, payload: dict[str, Any]) -> None:
    message = ChatMessage(
        session_id=session_id,
        role=str(payload.get("role") or "user"),
        content=str(payload.get("content") or ""),
        media_type=payload.get("media_type"),
        typing_speed=payload.get("typing_speed"),
        screen_time=payload.get("screen_time"),
        sentiment=payload.get("sentiment"),
        detected_emotion=payload.get("detected_emotion"),
        inferred_stress_level=payload.get("inferred_stress_level"),
    )
    db.add(message)
    db.commit()


def _serialize_message(message: ChatMessage) -> dict[str, Any]:
    return {
        "role": message.role,
        "content": message.content,
        "media_type": message.media_type,
        "typing_speed": message.typing_speed,
        "screen_time": message.screen_time,
        "sentiment": message.sentiment,
        "detected_emotion": message.detected_emotion,
        "inferred_stress_level": message.inferred_stress_level,
        "created_at": message.created_at.isoformat() if message.created_at else None,
    }


def _get_session_messages(db: Session, session_id: int) -> list[dict[str, Any]]:
    rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.id.asc())
        .all()
    )
    return [_serialize_message(row) for row in rows]


def _get_last_session_messages(db: Session, session_id: int, limit: int = 5) -> list[dict[str, Any]]:
    rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.id.desc())
        .limit(limit)
        .all()
    )
    return [_serialize_message(row) for row in reversed(rows)]


def _get_all_sessions(db: Session) -> dict[int, list[dict[str, Any]]]:
    sessions = db.query(ChatSession).order_by(ChatSession.id.asc()).all()
    result: dict[int, list[dict[str, Any]]] = {}
    for session in sessions:
        result[int(session.id)] = _get_session_messages(db, int(session.id))
    return result


def _to_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return [value]


def _extract_history_from_db(db_session: ChatSession) -> tuple[list[float], list[str]]:
    """Extract stress and emotion history from database session."""
    stress_map = {"low": 25.0, "moderate": 55.0, "high": 85.0}
    history_stress: list[float] = []
    history_emotions: list[str] = []

    for msg in db_session.messages:
        if msg.stress_score is not None:
            history_stress.append(float(msg.stress_score))
        elif msg.stress_level and msg.stress_level in stress_map:
            history_stress.append(stress_map[msg.stress_level])
        if msg.detected_emotion:
            history_emotions.append(msg.detected_emotion)

    return history_stress, history_emotions


@router.post("/message")
async def send_message(
    request: Request,
    db: Session = Depends(get_db),
    message: str | None = Form(default=None),
    media_type: str | None = Form(default=None),
    media: UploadFile | None = File(default=None),
    session_id: int | None = Form(default=None),
    user_id: int = Form(default=1),  # Default user for now
    age: int | None = Form(default=None),
    profession: str | None = Form(default=None),
    typing_speed: float | None = Form(default=None),
    screen_time: float | None = Form(default=None),
    sentiment: str | None = Form(default=None),
    emotion: str | None = Form(default=None),
    history_stress: str | None = Form(default=None),
    history_emotions: str | None = Form(default=None),
    trend_description: str | None = Form(default=None),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Send a message to the mental health chatbot and save to database."""
    payload_message = message
    payload_media_type = media_type or "text"
    payload_session_id = session_id
    payload_age = age
    payload_profession = profession
    payload_typing_speed = typing_speed
    payload_screen_time = screen_time
    payload_sentiment = sentiment
    payload_emotion = emotion
    payload_history_stress = history_stress
    payload_history_emotions = history_emotions
    payload_trend_description = trend_description
    media_content: bytes | None = None
    video_analysis: dict[str, Any] | None = None
    transcription_result: dict[str, Any] | None = None

    if request.headers.get("content-type", "").startswith("application/json"):
        body = await request.json()
        payload_message = body.get("message", payload_message)
        payload_media_type = body.get("media_type", payload_media_type)
        payload_session_id = body.get("session_id", payload_session_id)
        payload_age = body.get("age", payload_age)
        payload_profession = body.get("profession", payload_profession)
        payload_typing_speed = body.get("typing_speed", payload_typing_speed)
        payload_screen_time = body.get("screen_time", payload_screen_time)
        payload_sentiment = body.get("sentiment", payload_sentiment)
        payload_emotion = body.get("emotion", payload_emotion)
        payload_history_stress = body.get("history_stress", payload_history_stress)
        payload_history_emotions = body.get("history_emotions", payload_history_emotions)
        payload_trend_description = body.get("trend_description", payload_trend_description)
        user_id = body.get("user_id", user_id)

    if not payload_message:
        payload_message = "I need support"

    if media is not None:
        media_content = await media.read()

    if payload_media_type == "audio" and media is not None:
        transcription_result = _speech_to_text_service.transcribe_audio_bytes(
            media_content or b"",
            filename=media.filename,
        )
        transcribed_text = str(transcription_result.get("text") or "").strip()
        if transcribed_text:
            payload_message = transcribed_text
        elif payload_message in {None, "", "📎 Voice message"}:
            payload_message = "I sent a voice note but transcription was unavailable."

    if payload_media_type == "video" and media_content:
        video_analysis = _emotion_detection_service.detect_from_video_bytes(
            media_content,
            filename=media.filename,
        )
        # Let facial emotion enrich chat context when explicit emotion is not provided.
        if not payload_emotion:
            payload_emotion = str(video_analysis.get("emotion") or "neutral")
        if not payload_sentiment:
            payload_sentiment = "negative" if str(payload_emotion).lower() in {
                "sad",
                "angry",
                "anxious",
                "stressed",
                "overwhelmed",
                "fear",
            } else "neutral"

    if payload_session_id is None:
        payload_session_id = _create_session(db)
    elif not _session_exists(db, payload_session_id):
        payload_session_id = _create_session(db)

    existing_messages = _get_session_messages(db, payload_session_id)
    session_history_stress, session_history_emotions = _extract_history_from_session(existing_messages)

    resolved_history_stress = _to_list(payload_history_stress) or session_history_stress
    resolved_history_emotions = _to_list(payload_history_emotions) or session_history_emotions

    structured_context = {
        "age": payload_age,
        "profession": payload_profession,
        "typing_speed": payload_typing_speed,
        "screen_time": payload_screen_time,
        "sentiment": payload_sentiment,
        "emotion": payload_emotion,
        "history_stress": resolved_history_stress,
        "history_emotions": resolved_history_emotions,
        "trend_description": payload_trend_description,
    }

    _add_message(
        db,
        payload_session_id,
        {
            "role": "user",
            "content": payload_message,
            "media_type": payload_media_type,
            "typing_speed": payload_typing_speed,
            "screen_time": payload_screen_time,
            "sentiment": payload_sentiment,
            "detected_emotion": payload_emotion,
        },
    )

    # Keep prompt context focused and fresh: only the latest 5 records.
    context_messages = _get_last_session_messages(db, payload_session_id, limit=5)

    result = _chatbot_service.generate_response(
        payload_message,
        context=context_messages,
        media_type=payload_media_type,
        structured_context=structured_context,
    )
    response_text = result["response"]
    detected_emotion = result["detected_emotion"]
    confidence = result["confidence"]
    structured = result.get("structured", {})

    _add_message(
        db,
        payload_session_id,
        {
            "role": "assistant",
            "content": response_text,
            "media_type": "text",
            "detected_emotion": detected_emotion,
            "inferred_stress_level": structured.get("stress_level"),
        },
    )

    response_payload = {
        "response": response_text,
        "session_id": payload_session_id,
        "message_id": assistant_msg.id,
        "detected_emotion": detected_emotion,
        "confidence": confidence,
        "stress_score": stress_score,
        "stress_level": stress_level,
        "pipeline": result.get("pipeline", {}),
        "structured": structured,
    }
    if video_analysis is not None:
        response_payload["video_analysis"] = {
            "status": video_analysis.get("status", "fallback"),
            "emotion": video_analysis.get("emotion", "neutral"),
            "confidence": video_analysis.get("confidence", 0.0),
            "risk_level": video_analysis.get("risk_level", "low"),
        }
    if transcription_result is not None:
        response_payload["transcription"] = {
            "status": transcription_result.get("status", "fallback"),
            "text": str(transcription_result.get("text") or "").strip(),
            "confidence": transcription_result.get("confidence", 0.0),
            "source": transcription_result.get("source", "unknown"),
        }
        response_payload["audio_debug"] = {
            "audio_size_bytes": int(transcription_result.get("audio_size_bytes", 0) or 0),
            "filename": transcription_result.get("filename", media.filename if media else None),
            "reason": transcription_result.get("reason"),
        }
    return response_payload


@router.get("/history")
async def get_chat_history(
    session_id: int | None = None,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve chat history for the authenticated user."""
    if session_id is None:
        return {"sessions": _get_all_sessions(db)}
    return {"session_id": session_id, "messages": _get_session_messages(db, session_id)}
