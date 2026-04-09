"""
Stress record database model.
"""
from sqlalchemy import Column, Integer, Float, String
from app.db.base import Base


class StressRecord(Base):
    __tablename__ = "stress_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    stress_score = Column(Float, nullable=False)
    emotion = Column(String, nullable=True)
    typing_speed = Column(Float, nullable=True)
    screen_time = Column(Float, nullable=True)
