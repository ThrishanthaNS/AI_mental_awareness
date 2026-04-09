"""
Recommendation routes - personalized mental health recommendations.
"""
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/")
async def get_recommendations():
    """Get personalized recommendations based on user mood and history."""
    pass


@router.get("/resources")
async def get_resources():
    """Get curated mental health resources."""
    pass
