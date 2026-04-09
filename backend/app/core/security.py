"""
Security utilities - JWT token creation, password hashing.
"""
from datetime import datetime, timedelta
from typing import Optional


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    pass


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    pass


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    pass
