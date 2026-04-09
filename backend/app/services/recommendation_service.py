"""
Recommendation service - personalized mental health recommendations.
"""
from typing import List


class RecommendationService:
    """Service for generating personalized mental health recommendations."""

    def get_recommendations(self, user_id: int, mood_history: list) -> List[dict]:
        """Generate personalized recommendations based on user mood history."""
        pass

    def get_resources(self, category: str) -> List[dict]:
        """Get curated mental health resources by category."""
        pass

    def get_coping_strategies(self, emotion: str) -> List[str]:
        """Get coping strategies for a specific emotion."""
        pass
