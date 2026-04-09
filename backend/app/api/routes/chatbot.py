"""
Chatbot routes - conversational mental health support.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, File, Form, Request, UploadFile, Depends
from sqlalchemy.orm import Session

from app.services.chatbot_service import ChatbotService
from app.db.session import get_db
from app.models.session import ChatSession, ChatMessage
from app.schemas.chatbot import ChatMessageResponse, ChatMessageDetailedDB

router = APIRouter(prefix="/chat", tags=["Chatbot"])

_chatbot_service = ChatbotService()


def _normalize_stress_level(value: str | None) -> str | None:
    if not value:
        return None
    level = value.strip().lower()
    if level == "medium":
        return "moderate"
    if level in {"low", "moderate", "high"}:
        return level
    return None


def _score_from_level(level: str | None) -> float | None:
    mapping = {"low": 25.0, "moderate": 55.0, "high": 85.0}
    return mapping.get(level) if level else None


def _safe_iso(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt else None


def _build_recommendations(score: float) -> list[str]:
    if score >= 70:
        return [
            "Take a 10-minute break away from the screen now",
            "Reduce one non-urgent task from today's plan",
            "Do a short 4-4-6 breathing cycle for 2 minutes",
        ]
    if score >= 40:
        return [
            "Work in one focused block, then pause for 5 minutes",
            "Hydrate and do a brief shoulder/neck stretch",
            "Write your top 2 priorities for the next hour",
        ]
    return [
        "Keep current routines and continue short recovery breaks",
        "Capture one positive note from today",
        "Plan one relaxing activity for tonight",
    ]


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

    # Create or get chat session
    if payload_session_id is None:
        db_session = ChatSession(user_id=user_id, title="Chat Session")
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        payload_session_id = db_session.id
    else:
        db_session = db.query(ChatSession).filter(ChatSession.id == payload_session_id).first()
        if not db_session:
            db_session = ChatSession(user_id=user_id, title="Chat Session")
            db.add(db_session)
            db.commit()
            db.refresh(db_session)

    # Extract history from database
    session_history_stress, session_history_emotions = _extract_history_from_db(db_session)

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

    # Build message list from database
    db_messages = [
        {
            "role": msg.role,
            "content": msg.content,
            "detected_emotion": msg.detected_emotion,
            "stress_level": msg.stress_level,
            "stress_score": msg.stress_score,
        }
        for msg in db_session.messages
    ]

    # Save user message to database
    user_msg = ChatMessage(
        session_id=payload_session_id,
        role="user",
        content=payload_message,
        detected_emotion=payload_emotion,
        confidence=None,
        stress_score=None,
        stress_level=None,
    )
    db.add(user_msg)
    db.commit()

    # Generate response from chatbot service
    result = _chatbot_service.generate_response(
        payload_message,
        context=db_messages,
        media_type=payload_media_type,
        structured_context=structured_context,
    )
    response_text = result["response"]
    detected_emotion = result["detected_emotion"]
    confidence = result["confidence"]
    structured = result.get("structured", {})

    stress_level = _normalize_stress_level(result.get("stress_level"))
    if stress_level is None and isinstance(structured, dict):
        stress_level = _normalize_stress_level(structured.get("stress_level"))

    stress_score = result.get("stress_score")
    if stress_score is None:
        stress_score = _score_from_level(stress_level)

    # Save assistant message to database
    assistant_msg = ChatMessage(
        session_id=payload_session_id,
        role="assistant",
        content=response_text,
        detected_emotion=detected_emotion,
        confidence=confidence,
        stress_score=stress_score,
        stress_level=stress_level,
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    # Consume uploaded media stream when present to avoid dangling handles
    if media is not None:
        await media.read()

    return {
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


@router.get("/history")
async def get_chat_history(
    session_id: int | None = None,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve chat history for a session from database."""
    if session_id is None:
        # Return all sessions with basic info
        sessions = db.query(ChatSession).all()
        return {
            "sessions": [
                {
                    "id": s.id,
                    "title": s.title,
                    "created_at": s.created_at,
                    "updated_at": s.updated_at,
                    "message_count": len(s.messages),
                }
                for s in sessions
            ]
        }
    
    # Get specific session with all messages
    db_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    if not db_session:
        return {"error": "Session not found", "session_id": session_id}
    
    messages = [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "detected_emotion": msg.detected_emotion,
            "confidence": msg.confidence,
            "stress_score": msg.stress_score,
            "stress_level": msg.stress_level,
            "created_at": msg.created_at,
        }
        for msg in db_session.messages
    ]
    
    return {
        "session_id": session_id,
        "title": db_session.title,
        "created_at": db_session.created_at,
        "updated_at": db_session.updated_at,
        "messages": messages,
    }


@router.get("/sessions")
async def list_chat_sessions(
    user_id: int = 1,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """List all chat sessions for a user."""
    sessions = db.query(ChatSession).filter(ChatSession.user_id == user_id).all()
    
    return {
        "user_id": user_id,
        "sessions": [
            {
                "id": s.id,
                "title": s.title,
                "created_at": s.created_at,
                "updated_at": s.updated_at,
                "message_count": len(s.messages),
            }
            for s in sessions
        ],
    }


@router.post("/sessions")
async def create_chat_session(
    user_id: int,
    title: str | None = None,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Create a new chat session."""
    session = ChatSession(user_id=user_id, title=title or "New Chat Session")
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return {
        "id": session.id,
        "user_id": session.user_id,
        "title": session.title,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
    }


@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Delete a chat session and all its messages."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    if not session:
        return {"error": "Session not found", "session_id": session_id}
    
    db.delete(session)
    db.commit()
    
    return {"message": "Session deleted successfully", "session_id": session_id}


@router.get("/insights")
async def get_chat_insights(
    user_id: int = 1,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Compute dashboard insights from persisted chat messages."""
    sessions = db.query(ChatSession).filter(ChatSession.user_id == user_id).all()
    if not sessions:
        return {
            "user_id": user_id,
            "current_score": 0.0,
            "previous_score": 0.0,
            "risk_level": "low",
            "trend_data": [0.0],
            "day_labels": ["Today"],
            "signals": {
                "behavioral": {
                    "activity": "No chat activity yet",
                    "late_night_activity": "0 late-night messages",
                },
                "emotional": {
                    "dominant_emotion": "neutral",
                    "high_stress_ratio": "0%",
                },
                "contextual": {
                    "sessions": 0,
                    "messages": 0,
                    "user": f"User {user_id}",
                },
            },
            "risk_factors": [
                {"label": "No recent stress data", "value": "Start a chat to begin tracking", "icon": "ℹ️"}
            ],
            "recommendations": _build_recommendations(0.0),
            "peak_stress_time": "N/A",
            "intervention_time": "N/A",
            "burnout_risk": "LOW",
            "burnout_days": 14,
        }

    all_messages: list[ChatMessage] = []
    for session in sessions:
        all_messages.extend(session.messages)

    assistant_messages = [msg for msg in all_messages if msg.role == "assistant"]
    user_messages = [msg for msg in all_messages if msg.role == "user"]

    score_points: list[tuple[float, datetime | None]] = []
    for msg in assistant_messages:
        score = msg.stress_score
        if score is None:
            score = _score_from_level(_normalize_stress_level(msg.stress_level))
        if score is not None:
            score_points.append((float(score), msg.created_at))

    if not score_points:
        score_points = [(0.0, None)]

    latest_points = score_points[-7:]
    trend_data = [round(score, 2) for score, _ in latest_points]
    day_labels = [
        dt.strftime("%a") if dt else "N/A"
        for _, dt in latest_points
    ]

    current_score = latest_points[-1][0]
    previous_score = latest_points[-2][0] if len(latest_points) > 1 else current_score

    if current_score < 40:
        risk_level = "low"
    elif current_score < 60:
        risk_level = "medium"
    else:
        risk_level = "high"

    emotion_counter = Counter(
        (msg.detected_emotion or "neutral").strip().lower()
        for msg in assistant_messages
        if isinstance(msg.detected_emotion, str) and msg.detected_emotion.strip()
    )
    dominant_emotion = emotion_counter.most_common(1)[0][0] if emotion_counter else "neutral"

    high_count = sum(1 for score, _ in score_points if score >= 70)
    high_ratio = (high_count / max(len(score_points), 1)) * 100

    late_night_count = sum(
        1
        for msg in user_messages
        if msg.created_at and (msg.created_at.hour >= 22 or msg.created_at.hour <= 5)
    )
    activity_last_24h = sum(
        1
        for msg in user_messages
        if msg.created_at and (datetime.utcnow() - msg.created_at).total_seconds() <= 86400
    )

    peak_item = max(score_points, key=lambda pair: pair[0]) if score_points else (0.0, None)
    peak_time = peak_item[1]
    intervention_time = None
    intervention_window_minutes = 15
    if peak_time:
        intervention_time = peak_time - timedelta(minutes=intervention_window_minutes)

    risk_factors: list[dict[str, str]] = []
    if high_ratio >= 50:
        risk_factors.append({"label": "Frequent high stress", "value": f"{high_ratio:.0f}% of recent chats", "icon": "📈"})

    trend_delta = current_score - previous_score
    if trend_delta >= 8:
        risk_factors.append({"label": "Stress increasing", "value": f"+{trend_delta:.0f} vs previous", "icon": "⚠️"})
    elif trend_delta <= -8:
        risk_factors.append({"label": "Stress improving", "value": f"{trend_delta:.0f} vs previous", "icon": "✅"})

    if late_night_count > 0:
        risk_factors.append({"label": "Late-night activity", "value": f"{late_night_count} late-night chats", "icon": "🌙"})

    if not risk_factors:
        risk_factors.append({"label": "Balanced recent pattern", "value": "No major risk spike detected", "icon": "🟢"})

    burnout_days = 3 if risk_level == "high" else 7 if risk_level == "medium" else 14

    return {
        "user_id": user_id,
        "current_score": round(current_score, 2),
        "previous_score": round(previous_score, 2),
        "risk_level": risk_level,
        "trend_data": trend_data,
        "day_labels": day_labels,
        "signals": {
            "behavioral": {
                "activity": f"{activity_last_24h} user messages in last 24h",
                "late_night_activity": f"{late_night_count} late-night messages",
            },
            "emotional": {
                "dominant_emotion": dominant_emotion,
                "high_stress_ratio": f"{high_ratio:.0f}%",
            },
            "contextual": {
                "sessions": len(sessions),
                "messages": len(all_messages),
                "user": f"User {user_id}",
            },
        },
        "risk_factors": risk_factors,
        "recommendations": _build_recommendations(current_score),
        "peak_stress_time": peak_time.strftime("%I:%M %p") if peak_time else "N/A",
        "intervention_time": intervention_time.strftime("%I:%M %p") if intervention_time else "N/A",
        "intervention_window_minutes": intervention_window_minutes if peak_time else 0,
        "burnout_risk": risk_level.upper(),
        "burnout_days": burnout_days,
        "updated_at": _safe_iso(datetime.utcnow()),
    }
