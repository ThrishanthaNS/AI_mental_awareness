"""
Chatbot routes - conversational mental health support.
"""
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/chat", tags=["Chatbot"])


@router.post("/message")
async def send_message():
    """Send a message to the mental health chatbot."""
    pass


@router.get("/history")
async def get_chat_history():
    """Retrieve chat history for the authenticated user."""
    pass
