"""
Core stress scoring service used by the /analyze endpoint.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from app.core.config import get_settings
from app.services.llm_suggestion_service import LLMSuggestionService
from app.services.sentiment_service import SentimentService


RiskLevel = Literal["low", "medium", "high"]
VoiceStress = Literal["low", "high"]
FacialEmotion = Literal["neutral", "sad"]


@dataclass(frozen=True)
class ScoringWeights:
    typing: float = 0.25
    screen: float = 0.25
    text: float = 0.35
    voice: float = 0.10
    face: float = 0.05


_weights = ScoringWeights()
_settings = get_settings()
_sentiment_service = SentimentService()
_llm_suggestion_service = LLMSuggestionService()


class StressLogRegCalibrator:
    """Optional Logistic Regression calibrator loaded from ml/models."""

    def __init__(self):
        self.model = None
        self._attempted_load = False

    def _load_model(self):
        if self._attempted_load:
            return
        self._attempted_load = True

        try:
            import joblib

            project_root = Path(__file__).resolve().parents[3]
            model_path = project_root / "ml" / "models" / "stress_logreg.pkl"
            if model_path.exists():
                self.model = joblib.load(model_path)
        except Exception:
            self.model = None

    def predict_probability(self, features: list[float]) -> float | None:
        self._load_model()
        if self.model is None:
            return None

        try:
            if hasattr(self.model, "predict_proba"):
                return float(self.model.predict_proba([features])[0][1])
            # Fallback for models without predict_proba
            pred = float(self.model.predict([features])[0])
            return max(0.0, min(1.0, pred))
        except Exception:
            return None


_logreg_calibrator = StressLogRegCalibrator()


def _typing_stress_score(typing_speed: float) -> float:
    """
    Low typing speed can be a stress marker in this MVP.
    >= 55 WPM => 0 stress, <= 20 WPM => 100 stress, linear in-between.
    """
    if typing_speed >= 55:
        return 0.0
    if typing_speed <= 20:
        return 100.0
    ratio = (55 - typing_speed) / (55 - 20)
    return ratio * 100


def _screen_stress_score(screen_time: float) -> float:
    """
    Higher screen time tends to correlate with fatigue and stress.
    <= 3 hours => 0 stress, >= 12 hours => 100 stress.
    """
    if screen_time <= 3:
        return 0.0
    if screen_time >= 12:
        return 100.0
    ratio = (screen_time - 3) / (12 - 3)
    return ratio * 100


def _text_stress_score(text_input: str) -> tuple[float, dict]:
    """
    Convert signed sentiment score (-1 to +1) into stress.
    Negative sentiment increases stress, positive lowers it.
    """
    sentiment = _sentiment_service.analyze(text_input)
    signed_score = float(sentiment.get("signed_score", 0.0))
    stress = (1 - signed_score) / 2 * 100
    return max(0.0, min(100.0, stress)), sentiment


def _voice_stress_score(voice_stress: VoiceStress | None) -> float:
    if voice_stress is None:
        return 0.0
    return 100.0 if voice_stress == "high" else 0.0


def _facial_stress_score(facial_emotion: FacialEmotion | None) -> float:
    if facial_emotion is None:
        return 0.0
    return 85.0 if facial_emotion == "sad" else 0.0


def _risk_level(score: float) -> RiskLevel:
    if score >= 70:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


def _suggestion_for(level: RiskLevel) -> str:
    if level == "high":
        return (
            "High stress detected: pause for a 3-minute guided breathing exercise "
            "and reach out to a trusted person today."
        )
    if level == "medium":
        return (
            "Moderate stress detected: take a short walk, use focused work blocks, "
            "and reduce non-essential screen use for the next hour."
        )
    return (
        "Low stress detected: great balance today. Keep your routine and take small "
        "wellness breaks to stay resilient."
    )


def calculate_stress(
    *,
    typing_speed: float,
    screen_time: float,
    text_input: str,
    voice_stress: VoiceStress | None = None,
    facial_emotion: FacialEmotion | None = None,
) -> dict:
    """
    Returns a normalized stress output payload for the API.
    """
    typing_score = _typing_stress_score(typing_speed)
    screen_score = _screen_stress_score(screen_time)
    text_score, sentiment_meta = _text_stress_score(text_input)
    voice_score = _voice_stress_score(voice_stress)
    face_score = _facial_stress_score(facial_emotion)

    weighted_rule_score = (
        typing_score * _weights.typing
        + screen_score * _weights.screen
        + text_score * _weights.text
        + voice_score * _weights.voice
        + face_score * _weights.face
    )

    features = [
        typing_score,
        screen_score,
        text_score,
        voice_score,
        face_score,
        float(sentiment_meta.get("confidence", 0.5)) * 100,
    ]
    logreg_probability = _logreg_calibrator.predict_probability(features)

    if logreg_probability is None:
        stress_score = round(max(0.0, min(100.0, weighted_rule_score)), 2)
    else:
        logreg_score = logreg_probability * 100
        # Keep rule-based logic primary, blend calibrated ML score as enhancement.
        blended = 0.8 * weighted_rule_score + 0.2 * logreg_score
        stress_score = round(max(0.0, min(100.0, blended)), 2)

    risk_level = _risk_level(stress_score)
    llm_suggestion = _llm_suggestion_service.generate(
        stress_score=stress_score,
        risk_level=risk_level,
        text_input=text_input,
        breakdown={
            "typing": round(typing_score, 2),
            "screen_time": round(screen_score, 2),
            "text": round(text_score, 2),
            "voice": round(voice_score, 2),
            "facial": round(face_score, 2),
        },
    )
    suggestion = llm_suggestion or _suggestion_for(risk_level)

    return {
        "stress_score": stress_score,
        "risk_level": risk_level,
        "suggestion": suggestion,
        "breakdown": {
            "typing": round(typing_score, 2),
            "screen_time": round(screen_score, 2),
            "text": round(text_score, 2),
            "voice": round(voice_score, 2),
            "facial": round(face_score, 2),
        },
        "pipeline": {
            "sentiment_model": sentiment_meta.get("source", "unknown"),
            "logreg_calibration": bool(logreg_probability is not None),
            "llm_suggestion": bool(llm_suggestion),
            "llm_provider": "groq",
        },
    }
