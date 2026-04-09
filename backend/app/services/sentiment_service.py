"""
Sentiment analysis service.
"""
from __future__ import annotations

from app.core.config import get_settings
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class SentimentService:
    """Service for analyzing sentiment from text input.

    Primary: HuggingFace DistilBERT sentiment pipeline
    Fallback: VADER lexical sentiment
    """

    def __init__(self):
        self.settings = get_settings()
        self.model: SentimentIntensityAnalyzer | None = None
        self.hf_pipeline = None
        self.model_source = "vader"
        self.load_model()

    def load_model(self):
        """Load DistilBERT pipeline; fallback to VADER when unavailable."""
        self.model = SentimentIntensityAnalyzer()
        try:
            from transformers import pipeline

            self.hf_pipeline = pipeline(
                "sentiment-analysis",
                model=self.settings.HUGGINGFACE_SENTIMENT_MODEL,
            )
            self.model_source = "distilbert"
        except Exception:
            self.hf_pipeline = None
            self.model_source = "vader"

    @staticmethod
    def _signed_score_from_hf(label: str, confidence: float) -> float:
        if label.upper() == "POSITIVE":
            return confidence
        return -confidence

    def analyze(self, text: str) -> dict:
        """
        Analyze sentiment.

        Returns: {
            "sentiment": str,
            "confidence": float,
            "compound": float,
            "signed_score": float,
            "source": str
        }
        """
        if self.model is None:
            self.load_model()

        if self.hf_pipeline is not None:
            try:
                result = self.hf_pipeline(text[:512])[0]
                label = str(result.get("label", "NEUTRAL"))
                confidence = float(result.get("score", 0.5))
                signed = self._signed_score_from_hf(label, confidence)

                if signed >= 0.2:
                    sentiment = "positive"
                elif signed <= -0.2:
                    sentiment = "negative"
                else:
                    sentiment = "neutral"

                return {
                    "sentiment": sentiment,
                    "confidence": round(confidence, 3),
                    "compound": round(signed, 3),
                    "signed_score": round(signed, 3),
                    "source": "distilbert",
                }
            except Exception:
                # Fallback path below if runtime inference fails.
                pass

        scores = self.model.polarity_scores(text)
        compound = scores["compound"]

        if compound >= 0.05:
            sentiment = "positive"
            confidence = scores["pos"]
        elif compound <= -0.05:
            sentiment = "negative"
            confidence = scores["neg"]
        else:
            sentiment = "neutral"
            confidence = scores["neu"]

        return {
            "sentiment": sentiment,
            "confidence": round(float(confidence), 3),
            "compound": round(float(compound), 3),
            "signed_score": round(float(compound), 3),
            "source": "vader",
        }
