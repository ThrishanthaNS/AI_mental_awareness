"""
Authentication routes - login, register, token refresh.
"""
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
async def register():
    """Register a new user."""
    pass


@router.post("/login")
async def login():
    """Authenticate user and return JWT token."""
    pass


@router.post("/refresh")
async def refresh_token():
    """Refresh an expired access token."""
    pass
