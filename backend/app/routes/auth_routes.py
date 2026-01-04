"""
Authentication routes for the E-Learning Platform
Handles user authentication and session management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import Dict, Any, Optional
import logging

from app.dependencies.auth import get_current_user, get_current_admin_user
from app.core.logging import get_logger

logger = get_logger("auth_routes")
security = HTTPBearer()

router = APIRouter()


@router.get("/me")
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get current user information"""
    return {
        "uid": current_user["uid"],
        "email": current_user["email"],
        "role": current_user["role"],
        "email_verified": current_user["email_verified"]
    }


@router.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Logout user (revoke refresh tokens)"""
    logger.info(f"User logged out: {current_user['uid']}")
    return {"message": "Successfully logged out"}


@router.get("/verify")
async def verify_token(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Verify authentication token"""
    return {
        "valid": True,
        "uid": current_user["uid"],
        "email": current_user["email"],
        "role": current_user["role"]
    }