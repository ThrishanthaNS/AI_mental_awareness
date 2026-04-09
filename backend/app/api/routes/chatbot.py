"""
Chatbot routes - conversational mental health support.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, File, Form, Request, UploadFile
from app.services.chatbot_service import ChatbotService

router = APIRouter(prefix="/chat", tags=["Chatbot"])

_chat_sessions: dict[int, list[dict[str, str]]] = {}
_next_session_id = 1

_chatbot_service = ChatbotService()


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


def _extract_history_from_session(messages: list[dict[str, Any]]) -> tuple[list[float], list[str]]:
    stress_map = {"low": 25.0, "medium": 55.0, "high": 85.0}
    history_stress: list[float] = []
    history_emotions: list[str] = []

    for msg in messages:
        level = str(msg.get("inferred_stress_level", "")).lower()
        if level in stress_map:
            history_stress.append(stress_map[level])

        detected_emotion = msg.get("detected_emotion")
        if isinstance(detected_emotion, str) and detected_emotion.strip():
            history_emotions.append(detected_emotion.strip())

    return history_stress, history_emotions


@router.post("/message")
async def send_message(
    request: Request,
    message: str | None = Form(default=None),
    media_type: str | None = Form(default=None),
    media: UploadFile | None = File(default=None),
    session_id: int | None = Form(default=None),
    age: int | None = Form(default=None),
    profession: str | None = Form(default=None),
    typing_speed: float | None = Form(default=None),
    screen_time: float | None = Form(default=None),
    sentiment: str | None = Form(default=None),
    emotion: str | None = Form(default=None),
    history_stress: str | None = Form(default=None),
    history_emotions: str | None = Form(default=None),
    trend_description: str | None = Form(default=None),
) -> dict[str, Any]:
    """Send a message to the mental health chatbot."""
    payload_message = message
    payload_media_type = media_type
    payload_session_id = session_id
    payload_age: Any = age
    payload_profession = profession
    payload_typing_speed: Any = typing_speed
    payload_screen_time: Any = screen_time
    payload_sentiment = sentiment
    payload_emotion = emotion
    payload_history_stress: Any = history_stress
    payload_history_emotions: Any = history_emotions
    payload_trend_description = trend_description

    if request.headers.get("content-type", "").startswith("application/json"):
        body = await request.json()
        payload_message = body.get("message")
        payload_media_type = body.get("media_type", "text")
        payload_session_id = body.get("session_id")
        payload_age = body.get("age")
        payload_profession = body.get("profession")
        payload_typing_speed = body.get("typing_speed")
        payload_screen_time = body.get("screen_time")
        payload_sentiment = body.get("sentiment")
        payload_emotion = body.get("emotion")
        payload_history_stress = body.get("history_stress")
        payload_history_emotions = body.get("history_emotions")
        payload_trend_description = body.get("trend_description")

    if not payload_message:
        payload_message = "I need support"
    if not payload_media_type:
        payload_media_type = "text"

    global _next_session_id
    if payload_session_id is None:
        payload_session_id = _next_session_id
        _next_session_id += 1

    if payload_session_id not in _chat_sessions:
        _chat_sessions[payload_session_id] = []

    session_history_stress, session_history_emotions = _extract_history_from_session(_chat_sessions[payload_session_id])

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

    _chat_sessions[payload_session_id].append(
        {
            "role": "user",
            "content": payload_message,
            "media_type": payload_media_type,
            "typing_speed": payload_typing_speed,
            "screen_time": payload_screen_time,
            "sentiment": payload_sentiment,
            "detected_emotion": payload_emotion,
        }
    )

    result = _chatbot_service.generate_response(
        payload_message,
        context=_chat_sessions[payload_session_id],
        media_type=payload_media_type,
        structured_context=structured_context,
    )
    response_text = result["response"]
    detected_emotion = result["detected_emotion"]
    confidence = result["confidence"]
    structured = result.get("structured", {})

    _chat_sessions[payload_session_id].append(
        {
            "role": "assistant",
            "content": response_text,
            "media_type": "text",
            "detected_emotion": detected_emotion,
            "inferred_stress_level": structured.get("stress_level"),
        }
    )

    # Consume uploaded media stream when present to avoid dangling handles.
    if media is not None:
        await media.read()

    return {
        "response": response_text,
        "session_id": payload_session_id,
        "detected_emotion": detected_emotion,
        "confidence": confidence,
        "pipeline": result.get("pipeline", {}),
        "structured": structured,
    }


@router.get("/history")
async def get_chat_history(session_id: int | None = None) -> dict[str, Any]:
    """Retrieve chat history for the authenticated user."""
    if session_id is None:
        return {"sessions": _chat_sessions}
    return {"session_id": session_id, "messages": _chat_sessions.get(session_id, [])}
