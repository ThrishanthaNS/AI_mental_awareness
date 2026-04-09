"""
Optional Groq suggestion enhancement service.
"""
from __future__ import annotations

from app.core.config import get_settings


class LLMSuggestionService:
    def __init__(self):
        self.settings = get_settings()

    def generate(
        self,
        *,
        stress_score: float,
        risk_level: str,
        text_input: str,
        breakdown: dict[str, float],
    ) -> str | None:
        if not self.settings.ENABLE_GROQ_SUGGESTIONS or not self.settings.GROQ_API_KEY:
            return None

        prompt = (
            "You are a concise mental wellness assistant. Generate one practical, supportive, "
            "non-clinical suggestion in 1-2 short sentences. "
            f"Stress score: {stress_score}. Risk: {risk_level}. "
            f"Breakdown: {breakdown}. User text: {text_input[:400]}"
        )

        try:
            from groq import Groq

            client = Groq(api_key=self.settings.GROQ_API_KEY)
            models_to_try = [self.settings.GROQ_MODEL, self.settings.GROQ_FALLBACK_MODEL]
            tried = set()

            for model_name in models_to_try:
                if not model_name or model_name in tried:
                    continue
                tried.add(model_name)
                try:
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": "You are a concise mental wellness assistant."},
                            {"role": "user", "content": prompt},
                        ],
                        max_tokens=90,
                        temperature=0.4,
                    )
                    text = (response.choices[0].message.content or "").strip()
                    if text:
                        return text
                except Exception:
                    continue

            return None
        except Exception:
            return None
