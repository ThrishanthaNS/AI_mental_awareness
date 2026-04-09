"""
Model training pipeline.
"""
from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


def _generate_synthetic_training_data(n_samples: int = 1200) -> pd.DataFrame:
    """
    Generate synthetic stress training rows when no labeled dataset is available.

    Features are aligned with backend scoring outputs (0-100 scales).
    """
    rng = np.random.default_rng(42)
    typing = rng.uniform(0, 100, n_samples)
    screen = rng.uniform(0, 100, n_samples)
    text = rng.uniform(0, 100, n_samples)
    voice = rng.choice([0.0, 100.0], n_samples, p=[0.7, 0.3])
    facial = rng.choice([0.0, 85.0], n_samples, p=[0.75, 0.25])
    sentiment_conf = rng.uniform(40, 100, n_samples)

    weighted = 0.25 * typing + 0.25 * screen + 0.35 * text + 0.1 * voice + 0.05 * facial
    noisy = weighted + rng.normal(0, 7.5, n_samples)
    label = (noisy >= 60).astype(int)

    return pd.DataFrame(
        {
            "typing": typing,
            "screen_time": screen,
            "text": text,
            "voice": voice,
            "facial": facial,
            "sentiment_confidence": sentiment_conf,
            "stress_label": label,
        }
    )


def _load_stress_training_frame(data_path: str) -> pd.DataFrame:
    candidate = Path(data_path) / "stress_training.csv"
    if candidate.exists():
        return pd.read_csv(candidate)
    return _generate_synthetic_training_data()


def train_sentiment_model(data_path: str, output_path: str):
    """Train the sentiment analysis model."""
    # DistilBERT is used directly from HuggingFace at inference time.
    return None


def train_stress_model(data_path: str, output_path: str):
    """Train a logistic regression stress calibration model."""
    frame = _load_stress_training_frame(data_path)

    required_cols = [
        "typing",
        "screen_time",
        "text",
        "voice",
        "facial",
        "sentiment_confidence",
        "stress_label",
    ]
    missing = [col for col in required_cols if col not in frame.columns]
    if missing:
        raise ValueError(f"Missing required training columns: {missing}")

    x = frame[[
        "typing",
        "screen_time",
        "text",
        "voice",
        "facial",
        "sentiment_confidence",
    ]]
    y = frame["stress_label"].astype(int)

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = LogisticRegression(max_iter=1200)
    model.fit(x_train, y_train)

    preds = model.predict(x_test)
    accuracy = accuracy_score(y_test, preds)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output)

    return {"accuracy": round(float(accuracy), 4), "saved_to": str(output)}


def train_emotion_model(data_path: str, output_path: str):
    """Train the emotion detection model."""
    return None


if __name__ == "__main__":
    train_sentiment_model("../data/processed/", "../models/sentiment_model.pkl")
    result = train_stress_model("../data/processed/", "../models/stress_logreg.pkl")
    print(f"Stress Logistic Regression training result: {result}")
    train_emotion_model("../data/processed/", "../models/emotion_model.h5")
