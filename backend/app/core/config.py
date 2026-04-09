"""
Application configuration and settings.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "AI Mental Awareness"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./app.db"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ML Model paths
    SENTIMENT_MODEL_PATH: str = "../../ml/models/sentiment_model.pkl"
    STRESS_MODEL_PATH: str = "../../ml/models/stress_model.pkl"
    EMOTION_MODEL_PATH: str = "../../ml/models/emotion_model.h5"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
