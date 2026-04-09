"""
AI Mental Awareness - FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analyze, chatbot, mood, detection, recommendations
from app.core.config import get_settings

settings = get_settings()

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


@app.get("/")
async def root():
    return {"message": "Welcome to AI Mental Awareness API", "version": settings.APP_VERSION}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
