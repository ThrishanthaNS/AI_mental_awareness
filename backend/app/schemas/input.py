"""
Schemas for stress analysis request/response payloads.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class AnalyzeInput(BaseModel):
    typing_speed: float = Field(
        ...,
        ge=0,
        description="Typing speed in words per minute",
        examples=[42.0],
    )
    screen_time: float = Field(
        ...,
        ge=0,
        description="Daily screen time in hours",
        examples=[8.0],
    )
    text_input: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Short text describing mood/thoughts",
        examples=["I feel overwhelmed and tired with deadlines this week."],
    )
    voice_stress: Literal["low", "high"] | None = Field(
        default=None,
        description="Optional simulated voice stress signal",
        examples=["high"],
    )
    facial_emotion: Literal["neutral", "sad"] | None = Field(
        default=None,
        description="Optional simulated facial emotion signal",
        examples=["sad"],
    )


class AnalyzeOutput(BaseModel):
    stress_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Computed stress score from 0 to 100",
    )
    risk_level: Literal["low", "medium", "high"] = Field(
        ...,
        description="Risk band from stress score",
    )
    suggestion: str = Field(
        ...,
        description="Actionable recommendation based on risk",
    )
