"""
Core stress scoring service used by the /analyze endpoint.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


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


_analyzer = SentimentIntensityAnalyzer()
_weights = ScoringWeights()


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


def _text_stress_score(text_input: str) -> float:
    """
    Convert VADER compound sentiment into stress.
    Negative sentiment increases stress, positive lowers it.
    """
    compound = _analyzer.polarity_scores(text_input).get("compound", 0.0)
    stress = (1 - compound) / 2 * 100
    return max(0.0, min(100.0, stress))


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
) -> dict[str, float | str]:
    """
    Returns a normalized stress output payload for the API.
    """
    typing_score = _typing_stress_score(typing_speed)
    screen_score = _screen_stress_score(screen_time)
    text_score = _text_stress_score(text_input)
    voice_score = _voice_stress_score(voice_stress)
    face_score = _facial_stress_score(facial_emotion)

    weighted = (
        typing_score * _weights.typing
        + screen_score * _weights.screen
        + text_score * _weights.text
        + voice_score * _weights.voice
        + face_score * _weights.face
    )

    stress_score = round(max(0.0, min(100.0, weighted)), 2)
    risk_level = _risk_level(stress_score)
    suggestion = _suggestion_for(risk_level)

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
    }
