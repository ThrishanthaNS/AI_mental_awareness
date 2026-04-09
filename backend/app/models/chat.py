"""
Simple chat pair record model.
"""
from sqlalchemy import Column, Integer, String, Text
from app.db.base import Base


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    session_id = Column(Integer, nullable=True, index=True)
    emotion = Column(String, nullable=True)
