"""
Sentiment analysis service.
"""
from __future__ import annotations

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class SentimentService:
    """Service for analyzing sentiment from text input."""

    def __init__(self):
        self.model: SentimentIntensityAnalyzer | None = None
        self.load_model()

    def load_model(self):
        """Load the VADER sentiment analyzer."""
        self.model = SentimentIntensityAnalyzer()

    def analyze(self, text: str) -> dict:
        """
        Analyze sentiment of given text using VADER.

        Returns: {"sentiment": str, "confidence": float, "compound": float}
        """
        if self.model is None:
            self.load_model()

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
        }
