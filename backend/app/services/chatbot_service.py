"""
Chatbot service - handles conversational logic for mental health support.
"""


class ChatbotService:
    """Service for managing chatbot conversations."""

    def __init__(self):
        self.model = None

    def generate_response(self, user_message: str, context: list = None) -> str:
        """Generate a supportive response to the user's message."""
        pass

    def detect_crisis(self, message: str) -> bool:
        """Detect if the user's message indicates a mental health crisis."""
        pass
