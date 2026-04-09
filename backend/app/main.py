"""
AI Mental Awareness - FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.base import Base
from app.db.session import engine
from app import models  # noqa: F401
from app.api.routes import analyze, chatbot, mood, detection, recommendations
from app.core.config import get_settings
from app.db.session import engine
from app.db.base import Base

# Import all models to register them with Base
from app.models.user import User
from app.models.session import ChatSession, ChatMessage
from app.models.mood import MoodEntry

settings = get_settings()

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered mental health awareness and support platform",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include demo routers used by frontend integration
app.include_router(analyze.router, prefix="/api/v1")
app.include_router(analyze.router)
app.include_router(chatbot.router, prefix="/api/v1")
app.include_router(mood.router, prefix="/api/v1")
app.include_router(detection.router, prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")


@app.on_event("startup")
def create_db_tables() -> None:
    """Create SQLite tables at startup if they do not exist."""
    Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    return {"message": "Welcome to AI Mental Awareness API", "version": settings.APP_VERSION}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
