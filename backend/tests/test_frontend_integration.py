from fastapi.testclient import TestClient

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


def test_recommendations_endpoint_available():
    response = client.get("/api/v1/recommendations/")
    assert response.status_code == 200
    assert "recommendations" in response.json()
