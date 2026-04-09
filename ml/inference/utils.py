"""
ML inference utility functions.
"""
import re
import numpy as np


def clean_input(text: str) -> str:
    """Clean and normalize input text for model inference."""
    text = text.lower().strip()
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    return text


def softmax(logits: np.ndarray) -> np.ndarray:
    """Apply softmax to convert logits to probabilities."""
    exp_logits = np.exp(logits - np.max(logits))
    return exp_logits / exp_logits.sum()


def format_prediction(label: str, confidence: float) -> dict:
    """Format prediction output consistently."""
    return {
        "label": label,
        "confidence": round(confidence, 4),
    }
