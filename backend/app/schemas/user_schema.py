"""
Pydantic schemas for User-related API requests and responses
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.constants.roles import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    profile_picture_url: Optional[str] = None


class UserCreate(UserBase):
    password: Optional[str] = None
    role: Optional[UserRole] = UserRole.USER


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    profile_picture_url: Optional[str] = None


class UserResponse(UserBase):
    id: str
    uid: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserProfile(UserBase):
    id: str
    created_at: datetime
    total_purchases: int = 0
    total_feedback_given: int = 0

    class Config:
        from_attributes = True


class AdminUserResponse(UserResponse):
    last_login: Optional[datetime] = None
    is_email_verified: bool = False


class UserStats(BaseModel):
    total_users: int
    active_users: int
    admin_users: int
    new_users_this_month: int
    users_by_role: dict[str, int]
