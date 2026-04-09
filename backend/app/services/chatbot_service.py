"""
Chatbot service - handles conversational logic for mental health support.
"""
from __future__ import annotations

import re
from typing import Any

from app.core.config import get_settings
from app.services.sentiment_service import SentimentService


class ChatbotService:
    """Service for managing chatbot conversations."""

    def __init__(self):
        self.settings = get_settings()
        self.sentiment_service = SentimentService()

    @staticmethod
    def _to_list(value: Any) -> list[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        if isinstance(value, str):
            parsed = [item.strip() for item in value.split(",") if item.strip()]
            return parsed
        return [value]

    @staticmethod
    def _infer_trend_description(history_stress: list[float]) -> str:
        if len(history_stress) < 3:
            return "insufficient data"
        prev = history_stress[-3:-1]
        recent = history_stress[-2:]
        prev_avg = sum(prev) / len(prev)
        recent_avg = sum(recent) / len(recent)
        delta = recent_avg - prev_avg
        if delta > 7:
            return "stress trend increasing"
        if delta < -7:
            return "stress trend improving"
        return "stress trend stable"

    def _merge_structured_context(
        self,
        structured_context: dict[str, Any] | None,
        sentiment: dict[str, Any],
    ) -> dict[str, Any]:
        data = structured_context or {}

        history_stress_raw = self._to_list(data.get("history_stress"))
        history_stress: list[float] = []
        for item in history_stress_raw:
            try:
                history_stress.append(float(item))
            except (TypeError, ValueError):
                continue

        history_emotions = [str(item) for item in self._to_list(data.get("history_emotions"))]

        trend_description = str(data.get("trend_description") or "").strip()
        if not trend_description:
            trend_description = self._infer_trend_description(history_stress)

        merged = {
            "age": data.get("age", "unknown"),
            "profession": data.get("profession", "unknown"),
            "typing_speed": data.get("typing_speed", "unknown"),
            "screen_time": data.get("screen_time", "unknown"),
            "sentiment": data.get("sentiment") or sentiment.get("sentiment", "neutral"),
            "emotion": data.get("emotion") or sentiment.get("sentiment", "neutral"),
            "history_stress": history_stress if history_stress else ["not available"],
            "history_emotions": history_emotions if history_emotions else ["not available"],
            "trend_description": trend_description,
        }
        return merged

    def _build_advanced_prompt(
        self,
        user_message: str,
        structured_context: dict[str, Any],
        recent_context: str,
    ) -> str:
        return (
            "You are an intelligent mental well-being assistant.\n\n"
            "Analyze the user holistically using multiple signals.\n\n"
            "-----------------------\n"
            "USER PROFILE:\n"
            f"- Age: {structured_context['age']}\n"
            f"- Profession: {structured_context['profession']}\n\n"
            "BEHAVIORAL SIGNALS:\n"
            f"- Typing Speed: {structured_context['typing_speed']}\n"
            f"- Screen Time (hours/day): {structured_context['screen_time']}\n\n"
            "EMOTIONAL SIGNALS:\n"
            f"- Current Sentiment: {structured_context['sentiment']}\n"
            f"- Detected Emotion: {structured_context['emotion']}\n\n"
            "HISTORICAL CONTEXT:\n"
            f"- Past Stress Scores: {structured_context['history_stress']}\n"
            f"- Past Emotions: {structured_context['history_emotions']}\n"
            f"- Trend: {structured_context['trend_description']}\n\n"
            "RECENT CONVERSATION (LAST 5 RECORDS):\n"
            f"{recent_context}\n\n"
            "CURRENT MESSAGE:\n"
            f'"{user_message}"\n\n'
            "-----------------------\n\n"
            "TASK:\n\n"
            "1. Infer:\n"
            "   - Stress Level (Low / Medium / High)\n"
            "   - Stress Score (0-100)\n"
            "   - Emotional State (1-2 words)\n\n"
            "2. Reason:\n"
            "   - Briefly explain why the user is in this state (based on signals + history)\n\n"
            "3. Respond:\n"
            "   - Give a short, natural, supportive response (1-2 sentences)\n\n"
            "4. Suggest:\n"
            "   - ONE actionable step (practical, not generic)\n\n"
            "-----------------------\n\n"
            "OUTPUT FORMAT (STRICT):\n\n"
            "Stress Level: <Low/Medium/High>\n"
            "Stress Score: <0-100>\n"
            "Emotion: <emotion>\n\n"
            "Reason: <1 short line>\n\n"
            "Response: <natural human response>\n\n"
            "Action: <one simple action>"
        )

    @staticmethod
    def _format_recent_context(context: list | None, limit: int = 5) -> str:
        if not context:
            return "No previous records available."

        recent = context[-limit:]
        lines: list[str] = []
        for item in recent:
            if not isinstance(item, dict):
                continue
            role = str(item.get("role") or "unknown").strip().lower()
            content = str(item.get("content") or "").strip()
            if not content:
                continue
            label = "User" if role == "user" else "Assistant"
            lines.append(f"- {label}: {content}")

        if not lines:
            return "No previous records available."
        return "\n".join(lines)

    @staticmethod
    def _parse_structured_output(text: str) -> dict[str, str]:
        parsed: dict[str, str] = {}
        patterns = {
            "stress_level": r"Stress\s*Level\s*:\s*(.*?)(?=\s*Emotion\s*:|\s*Reason\s*:|\s*Response\s*:|\s*Action\s*:|$)",
            "stress_score": r"Stress\s*Score\s*:\s*(.*?)(?=\s*Emotion\s*:|\s*Reason\s*:|\s*Response\s*:|\s*Action\s*:|$)",
            "emotion": r"Emotion\s*:\s*(.*?)(?=\s*Reason\s*:|\s*Response\s*:|\s*Action\s*:|$)",
            "reason": r"Reason\s*:\s*(.*?)(?=\s*Response\s*:|\s*Action\s*:|$)",
            "response": r"Response\s*:\s*(.*?)(?=\s*Action\s*:|$)",
            "action": r"Action\s*:\s*(.*)$",
        }
        for key, pattern in patterns.items():
            match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
            if match:
                parsed[key] = re.sub(r"\s+", " ", match.group(1)).strip()
        return parsed

    @staticmethod
    def _format_structured_output(parsed: dict[str, str]) -> str:
        return (
            f"Stress Level: {parsed.get('stress_level', 'Medium')}\n"
            f"Stress Score: {parsed.get('stress_score', '55')}\n"
            f"Emotion: {parsed.get('emotion', 'neutral')}\n\n"
            f"Reason: {parsed.get('reason', 'Multiple signals indicate moderate strain.')}\n\n"
            f"Response: {parsed.get('response', 'You are handling a lot, and your feelings make sense.')}\n\n"
            f"Action: {parsed.get('action', 'Take 3 slow breaths and list one next task to do now.')}"
        )

    @staticmethod
    def _stress_level_from_score(score: float) -> str:
        if score >= 70:
            return "High"
        if score >= 40:
            return "Medium"
        return "Low"

    @staticmethod
    def _normalize_score(value: Any) -> float | None:
        try:
            if isinstance(value, str):
                value = value.replace("%", "").strip()
            num = float(value)
            return max(0.0, min(100.0, num))
        except (TypeError, ValueError):
            return None

    def _compute_intelligent_stress_score(
        self,
        user_message: str,
        merged_context: dict[str, Any],
        sentiment: dict[str, Any],
        parsed: dict[str, str] | None = None,
    ) -> float:
        score = 50.0
        text = user_message.lower()

        # Sentiment + confidence are primary drivers.
        sentiment_label = str(merged_context.get("sentiment") or sentiment.get("sentiment", "neutral")).lower()
        confidence = float(sentiment.get("confidence", 0.65))
        if sentiment_label == "negative":
            score += 28.0 * confidence
        elif sentiment_label == "positive":
            score -= 24.0 * confidence

        severe_terms = {
            "panic", "overwhelmed", "breakdown", "burnout", "can't cope", "cannot cope", "hopeless"
        }
        moderate_terms = {
            "stressed", "stress", "anxious", "worried", "tired", "pressure", "deadline", "exhausted"
        }
        calming_terms = {"calm", "better", "relaxed", "good", "okay", "fine", "managed"}

        score += 15.0 * sum(1 for t in severe_terms if t in text)
        score += 8.0 * sum(1 for t in moderate_terms if t in text)
        score -= 6.0 * sum(1 for t in calming_terms if t in text)

        # Behavioral/context signals when provided.
        try:
            typing_speed = float(merged_context.get("typing_speed"))
            if typing_speed < 30:
                score += 8
            elif typing_speed > 75:
                score += 4
            elif typing_speed > 50:
                score -= 3
        except (TypeError, ValueError):
            pass

        try:
            screen_time = float(merged_context.get("screen_time"))
            if screen_time > 10:
                score += 14
            elif screen_time > 7:
                score += 8
            elif screen_time < 3:
                score -= 5
        except (TypeError, ValueError):
            pass

        history = merged_context.get("history_stress") or []
        if isinstance(history, list):
            numeric_history: list[float] = []
            for val in history:
                try:
                    numeric_history.append(float(val))
                except (TypeError, ValueError):
                    continue
            if numeric_history:
                history_avg = sum(numeric_history[-5:]) / min(len(numeric_history), 5)
                score = 0.75 * score + 0.25 * history_avg

        trend = str(merged_context.get("trend_description", "")).lower()
        if "increasing" in trend or "wors" in trend:
            score += 8
        elif "improving" in trend:
            score -= 8

        # Blend model-declared level/score when present.
        parsed = parsed or {}
        parsed_score = self._normalize_score(parsed.get("stress_score"))
        if parsed_score is not None:
            score = 0.65 * score + 0.35 * parsed_score

        parsed_level = str(parsed.get("stress_level", "")).strip().lower()
        if parsed_level in {"low", "medium", "high"}:
            target = {"low": 25.0, "medium": 55.0, "high": 82.0}[parsed_level]
            score = 0.8 * score + 0.2 * target

        return round(max(0.0, min(100.0, score)), 2)

    @staticmethod
    def _fallback_structured_output(
        user_message: str,
        merged_context: dict[str, Any],
        sentiment: dict[str, Any],
    ) -> tuple[str, dict[str, str]]:
        score = 50.0

        try:
            typing_speed = float(merged_context.get("typing_speed"))
            if typing_speed < 30:
                score += 15
            elif typing_speed > 70:
                score -= 10
        except (TypeError, ValueError):
            pass

        try:
            screen_time = float(merged_context.get("screen_time"))
            if screen_time > 9:
                score += 20
            elif screen_time > 6:
                score += 10
            elif screen_time < 3:
                score -= 8
        except (TypeError, ValueError):
            pass

        sentiment_label = str(merged_context.get("sentiment") or sentiment.get("sentiment", "neutral")).lower()
        if sentiment_label == "negative":
            score += 15
        elif sentiment_label == "positive":
            score -= 12

        emotion_label = str(merged_context.get("emotion", "neutral")).lower()
        if emotion_label in {"stressed", "anxious", "sad", "overwhelmed"}:
            score += 12
        elif emotion_label in {"calm", "happy", "relaxed"}:
            score -= 10

        trend = str(merged_context.get("trend_description", "")).lower()
        if "increasing" in trend or "wors" in trend:
            score += 10
        if "improving" in trend:
            score -= 8

        score = max(0.0, min(100.0, score))
        if score >= 70:
            stress_level = "High"
        elif score >= 40:
            stress_level = "Medium"
        else:
            stress_level = "Low"

        emotion_text = str(merged_context.get("emotion", sentiment.get("sentiment", "neutral")))
        reason = "Signals and history suggest your current load is affecting emotional balance."
        if stress_level == "High":
            response = "You are carrying a lot right now, and it is okay to slow down for a moment."
            action = "Pause for 2 minutes, breathe slowly, then start only your smallest pending task."
        elif stress_level == "Medium":
            response = "You seem under moderate pressure, but this is manageable with a small reset."
            action = "Take a 5-minute break away from the screen and return with one clear priority."
        else:
            response = "You appear relatively steady right now, and maintaining your routine can help."
            action = "Keep your momentum by scheduling one short recovery break in the next hour."

        parsed = {
            "stress_level": stress_level,
            "stress_score": f"{round(score, 2)}",
            "emotion": emotion_text,
            "reason": reason,
            "response": response,
            "action": action,
        }
        return ChatbotService._format_structured_output(parsed), parsed

    @staticmethod
    def _is_short_ack(message: str) -> bool:
        text = message.lower().strip()
        tokens = re.findall(r"[a-z']+", text)
        short_ack_keywords = {
            "ok",
            "okay",
            "kk",
            "k",
            "hmm",
            "hmmm",
            "y",
            "yes",
            "yeah",
            "yep",
            "no",
            "ee",
        }
        return len(tokens) <= 2 and (set(tokens) <= short_ack_keywords or len(text) <= 3)

    @staticmethod
    def _is_greeting(message: str) -> bool:
        text = message.lower().strip()
        tokens = set(re.findall(r"[a-z']+", text))
        return bool(tokens & {"hi", "hello", "hey"}) or text in {
            "good morning",
            "good afternoon",
            "good evening",
        }

    @staticmethod
    def _synthesize_from_model_signals(user_message: str, sentiment: dict, media_type: str) -> str:
        """
        Build response from model signals and user input without canned reply banks.
        """
        sentiment_label = str(sentiment.get("sentiment", "neutral"))
        confidence = float(sentiment.get("confidence", 0.65))
        source = str(sentiment.get("source", "model"))
        trimmed = " ".join(user_message.strip().split())[:180]

        if ChatbotService._is_short_ack(user_message):
            focus = "please share one clear feeling or trigger from today"
        elif ChatbotService._is_greeting(user_message):
            focus = "tell me how your mind and energy feel right now"
        elif sentiment_label == "negative":
            focus = "try a 60-second slow breathing cycle, then do one small next step"
        elif sentiment_label == "positive":
            focus = "keep momentum with short breaks and hydration"
        else:
            focus = "describe one concrete stress point so we can make a focused plan"

        media_hint = "using voice/video" if media_type in {"audio", "video"} else "in text"
        return (
            f"From your message {media_hint}, sentiment model ({source}) reads {sentiment_label} "
            f"at confidence {confidence:.2f}. You said: '{trimmed}'. Next step: {focus}."
        )

    def _generate_groq_response(
        self,
        user_message: str,
        context: list | None,
        media_type: str,
        sentiment: dict,
        structured_context: dict[str, Any] | None = None,
    ) -> str | None:
        if not self.settings.GROQ_API_KEY:
            return None

        try:
            from groq import Groq

            client = Groq(api_key=self.settings.GROQ_API_KEY)
            merged_context = self._merge_structured_context(structured_context, sentiment)
            recent_context = self._format_recent_context(context, limit=5)
            prompt = self._build_advanced_prompt(user_message, merged_context, recent_context)

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
                            {
                                "role": "system",
                                "content": (
                                    "You are a calm mental wellness support assistant. "
                                    "Follow the requested output format exactly."
                                ),
                            },
                            {"role": "user", "content": prompt},
                        ],
                        max_tokens=220,
                        temperature=0.2,
                    )
                    text = (response.choices[0].message.content or "").strip()
                    if text:
                        return text
                except Exception:
                    continue

            return None
        except Exception:
            return None

    def generate_response(
        self,
        user_message: str,
        context: list | None = None,
        media_type: str = "text",
        structured_context: dict[str, Any] | None = None,
    ) -> dict:
        """Generate a supportive response using model-first, fallback-safe logic."""
        sentiment = self.sentiment_service.analyze(user_message)
        merged_context = self._merge_structured_context(structured_context, sentiment)

        if self.detect_crisis(user_message):
            crisis_prompt = (
                "User may be at crisis risk. Respond in 1-2 short sentences with immediate safety-first advice, "
                "non-judgmental and urgent, including seeking local emergency or trusted human support now. "
                f"Message: {user_message}"
            )
            crisis_response = self._generate_groq_response(
                crisis_prompt,
                context,
                media_type,
                sentiment,
                structured_context=structured_context,
            )
            if crisis_response:
                parsed_crisis = self._parse_structured_output(crisis_response)
                normalized_crisis = (
                    self._format_structured_output(parsed_crisis)
                    if parsed_crisis
                    else crisis_response
                )
                crisis_score = max(
                    90.0,
                    self._compute_intelligent_stress_score(user_message, merged_context, sentiment, parsed_crisis),
                )
                return {
                    "response": normalized_crisis,
                    "detected_emotion": parsed_crisis.get("emotion", "crisis_risk"),
                    "confidence": 0.95,
                    "stress_score": crisis_score,
                    "stress_level": "high",
                    "pipeline": {
                        "sentiment_model": sentiment.get("source", "unknown"),
                        "groq_chat": True,
                        "fallback": False,
                        "structured_context": True,
                    },
                    "structured": parsed_crisis,
                }

            fallback_text, fallback_structured = self._fallback_structured_output(user_message, merged_context, sentiment)
            fallback_score = self._compute_intelligent_stress_score(
                user_message,
                merged_context,
                sentiment,
                fallback_structured,
            )
            return {
                "response": fallback_text,
                "detected_emotion": fallback_structured.get("emotion", "crisis_risk"),
                "confidence": 0.95,
                "stress_score": fallback_score,
                "stress_level": self._stress_level_from_score(fallback_score).lower(),
                "pipeline": {
                    "sentiment_model": sentiment.get("source", "unknown"),
                    "groq_chat": False,
                    "fallback": True,
                    "structured_context": True,
                },
                "structured": fallback_structured,
            }

        llm_response = self._generate_groq_response(
            user_message,
            context,
            media_type,
            sentiment,
            structured_context=structured_context,
        )
        if llm_response:
            parsed = self._parse_structured_output(llm_response)
            intelligent_score = self._compute_intelligent_stress_score(user_message, merged_context, sentiment, parsed)
            parsed["stress_score"] = str(intelligent_score)
            parsed["stress_level"] = self._stress_level_from_score(intelligent_score)
            normalized_response = (
                self._format_structured_output(parsed)
                if parsed
                else llm_response
            )
            return {
                "response": normalized_response,
                "detected_emotion": parsed.get("emotion", "neutral"),
                "confidence": sentiment.get("confidence", 0.75),
                "stress_score": intelligent_score,
                "stress_level": self._stress_level_from_score(intelligent_score).lower(),
                "pipeline": {
                    "sentiment_model": sentiment.get("source", "unknown"),
                    "groq_chat": True,
                    "fallback": False,
                    "structured_context": True,
                },
                "structured": parsed,
            }

        response, parsed = self._fallback_structured_output(user_message, merged_context, sentiment)
        intelligent_score = self._compute_intelligent_stress_score(user_message, merged_context, sentiment, parsed)
        parsed["stress_score"] = str(intelligent_score)
        parsed["stress_level"] = self._stress_level_from_score(intelligent_score)
        emotion = str(parsed.get("emotion", sentiment.get("sentiment", "neutral")))
        confidence = float(sentiment.get("confidence", 0.68))
        return {
            "response": response,
            "detected_emotion": emotion,
            "confidence": confidence,
            "stress_score": intelligent_score,
            "stress_level": self._stress_level_from_score(intelligent_score).lower(),
            "pipeline": {
                "sentiment_model": sentiment.get("source", "unknown"),
                "groq_chat": False,
                "fallback": True,
                "structured_context": True,
            },
            "structured": parsed,
        }

    def detect_crisis(self, message: str) -> bool:
        """Detect if the user's message indicates a mental health crisis."""
        text = message.lower()
        crisis_terms = {
            "suicide",
            "kill myself",
            "end my life",
            "self harm",
            "self-harm",
            "want to die",
            "hurt myself",
        }
        return any(term in text for term in crisis_terms)
