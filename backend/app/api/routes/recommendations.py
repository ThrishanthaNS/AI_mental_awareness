"""
Recommendation routes - personalized mental health recommendations.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/")
async def get_recommendations():
    """Get personalized recommendations based on user mood and history."""
    return {
        "recommendations": [
            "Take a 5-minute breathing break every 90 minutes.",
            "Use focused work blocks (25 min) and short resets.",
            "Avoid screens 30 minutes before sleep.",
        ]
    }


@router.get("/resources")
async def get_resources():
    """Get curated mental health resources."""
    return {
        "resources": [
            {
                "title": "Guided Breathing Exercise",
                "type": "video",
                "url": "https://example.com/breathing",
            },
            {
                "title": "Stress Management Basics",
                "type": "article",
                "url": "https://example.com/stress-basics",
            },
        ]
    }
