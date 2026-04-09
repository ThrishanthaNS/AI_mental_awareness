"""
Thin service wrapper around scoring logic.
"""
from __future__ import annotations

from app.services.scoring import calculate_stress


def analyze(
    typing_speed: float,
    screen_time: float,
    text_input: str,
    voice_stress: str | None = None,
    facial_emotion: str | None = None,
) -> dict[str, float | str]:
    return calculate_stress(
        typing_speed=typing_speed,
        screen_time=screen_time,
        text_input=text_input,
        voice_stress=voice_stress,
        facial_emotion=facial_emotion,
    )
