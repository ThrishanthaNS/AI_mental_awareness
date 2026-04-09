from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_analyze_low_risk_payload():
    payload = {
        "typing_speed": 62,
        "screen_time": 2.5,
        "text_input": "I had a good day and feel focused.",
        "voice_stress": "low",
        "facial_emotion": "neutral",
    }

    response = client.post("/analyze", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert 0 <= body["stress_score"] <= 100
    assert body["risk_level"] in {"low", "medium", "high"}
    assert isinstance(body["suggestion"], str) and len(body["suggestion"]) > 0


def test_analyze_high_risk_payload():
    payload = {
        "typing_speed": 18,
        "screen_time": 12,
        "text_input": "I feel overwhelmed, exhausted, and very anxious.",
        "voice_stress": "high",
        "facial_emotion": "sad",
    }

    response = client.post("/analyze", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["risk_level"] == "high"
    assert body["stress_score"] >= 70
