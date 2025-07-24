from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    """Base user model with common fields"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    avatar_url: Optional[str] = None



class UserOAuth(UserBase):
    """Model for OAuth user creation/updates"""
    provider: str
    provider_user_id: str
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    avatar_url: Optional[str] = None

class UserInDB(UserBase):
    """User model as stored in database"""
    id: UUID
    provider: str
    provider_user_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UserResponse(UserBase):
    """User model for API responses"""
    id: UUID
    provider: str
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True 