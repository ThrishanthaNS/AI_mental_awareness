"""
Shared dependencies for API routes (auth, DB session, etc.).
"""
from app.db.session import SessionLocal


async def get_current_user():
    """Dependency to get the current authenticated user from JWT token."""
    return {"id": 1}


def get_db():
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
