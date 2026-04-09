"""
/analyze route — accepts behavioural + textual signals, returns stress analysis.
"""
from fastapi import APIRouter, status

from app.schemas.input import AnalyzeInput, AnalyzeOutput
from app.services.analysis_service import analyze

router = APIRouter(tags=["Analysis"])


@router.post(
    "/analyze",
    response_model=AnalyzeOutput,
    status_code=status.HTTP_200_OK,
    summary="Analyze mental health signals",
    description=(
        "Accepts typing speed, daily screen time, and free-text input. "
        "Returns a stress score (0–100), risk level, and an actionable suggestion."
    ),
)
async def analyze_mental_health(payload: AnalyzeInput) -> AnalyzeOutput:
    result = analyze(
        typing_speed=payload.typing_speed,
        screen_time=payload.screen_time,
        text_input=payload.text_input,
        voice_stress=payload.voice_stress,
        facial_emotion=payload.facial_emotion,
    )
    return AnalyzeOutput(**result)
