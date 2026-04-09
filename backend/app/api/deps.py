"""
Shared dependencies for API routes (auth, DB session, etc.).
"""
from fastapi import Depends, HTTPException, status


async def get_current_user():
    """Dependency to get the current authenticated user from JWT token."""
    pass


async def get_db():
    """Dependency to get a database session."""
    pass
