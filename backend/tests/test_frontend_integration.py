from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app


client = TestClient(app)


def test_chat_message_json_contract():
    response = client.post(
        "/api/v1/chat/message",
        json={"message": "I am feeling stressed", "media_type": "text", "session_id": None},
    )
    assert response.status_code == 200
    body = response.json()
    assert "response" in body
    assert "session_id" in body


def test_chat_message_with_structured_context_contract():
    response = client.post(
        "/api/v1/chat/message",
        json={
            "message": "I have been overwhelmed this week.",
            "media_type": "text",
            "age": 24,
            "profession": "student",
            "typing_speed": 27,
            "screen_time": 9.5,
            "sentiment": "negative",
            "emotion": "anxious",
            "history_stress": [58, 64, 72],
            "history_emotions": ["stressed", "anxious", "overwhelmed"],
            "trend_description": "stress trend increasing",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert "structured" in body
    assert "response" in body


def test_mood_and_detection_endpoints_available():
    mood_response = client.post(
        "/api/v1/mood/log",
        json={"mood": "anxious", "intensity": 0.7, "notes": "Busy week"},
    )
    assert mood_response.status_code == 200

    detect_response = client.post("/api/v1/detect/text", json={"text": "I feel overwhelmed"})
    assert detect_response.status_code == 200
    assert "emotion" in detect_response.json()

    media_response = client.post(
        "/api/v1/detect/media",
        files={"file": ("frame.jpg", b"fake-image-bytes", "image/jpeg")},
    )
    assert media_response.status_code == 200
    media_body = media_response.json()
    assert "status" in media_body
    assert "emotion" in media_body
    assert "confidence" in media_body
    assert "risk_level" in media_body


def test_recommendations_endpoint_available():
    response = client.get("/api/v1/recommendations/")
    assert response.status_code == 200
    assert "recommendations" in response.json()


def test_chat_video_contract_contains_analysis():
    response = client.post(
        "/api/v1/chat/message",
        data={"message": "Analyze my expression", "media_type": "video"},
        files={"media": ("frame.jpg", b"fake-image-bytes", "image/jpeg")},
    )
    assert response.status_code == 200
    body = response.json()
    assert "video_analysis" in body
    assert set(body["video_analysis"].keys()) == {"status", "emotion", "confidence", "risk_level"}


def test_chat_audio_flow_transcribes_voice_to_text():
    with patch(
        "app.api.routes.chatbot._speech_to_text_service.transcribe_audio_bytes",
        return_value={
            "status": "success",
            "text": "I am feeling anxious today",
            "confidence": 0.91,
            "source": "groq_whisper",
        },
    ):
        response = client.post(
            "/api/v1/chat/message",
            data={"message": "📎 Voice message", "media_type": "audio"},
            files={"media": ("voice.wav", b"fake-audio-bytes", "audio/wav")},
        )

    assert response.status_code == 200
    body = response.json()
    assert "transcription" in body
    assert body["transcription"]["status"] == "success"
    assert body["transcription"]["text"] == "I am feeling anxious today"
    assert "audio_debug" in body
    assert isinstance(body["audio_debug"].get("audio_size_bytes"), int)
