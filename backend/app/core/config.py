from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
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
    STRESS_LOGREG_MODEL_PATH: str = "../../ml/models/stress_logreg.pkl"
    HUGGINGFACE_SENTIMENT_MODEL: str = "distilbert-base-uncased-finetuned-sst-2-english"

    # Groq LLM
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    GROQ_FALLBACK_MODEL: str = "llama-3.1-8b-instant"
    ENABLE_GROQ_SUGGESTIONS: bool = True

    # Resolve env from backend/.env first, then project-root .env.
    model_config = SettingsConfigDict(
        env_file=(
            str(Path(__file__).resolve().parents[2] / ".env"),
            str(Path(__file__).resolve().parents[3] / ".env"),
        ),
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()