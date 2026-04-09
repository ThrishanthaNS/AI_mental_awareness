"""
Model training pipeline.
"""


def train_sentiment_model(data_path: str, output_path: str):
    """Train the sentiment analysis model."""
    pass


def train_stress_model(data_path: str, output_path: str):
    """Train the stress detection model."""
    pass


def train_emotion_model(data_path: str, output_path: str):
    """Train the emotion detection model."""
    pass


if __name__ == "__main__":
    train_sentiment_model("../data/processed/", "../models/sentiment_model.pkl")
    train_stress_model("../data/processed/", "../models/stress_model.pkl")
    train_emotion_model("../data/processed/", "../models/emotion_model.h5")
