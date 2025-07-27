from pydantic import BaseModel, EmailStr, HttpUrl, validator
from typing import Optional, Literal, Union
from datetime import datetime
from uuid import UUID
from enum import Enum

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

class FileType(str, Enum):
    """Enum for supported file types"""
    PDF = "pdf"
    WORD = "word"

class LinkType(str, Enum):
    """Enum for supported link types"""
    BLOG = "blog"
    TWITTER = "twitter"
    YOUTUBE = "youtube"
    GITHUB = "github"
    REDDIT = "reddit"
    OTHER = "other"

class FileBase(BaseModel):
    """Base file model with common fields"""
    name: str
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    is_public: bool = False

class FileUpload(FileBase):
    """Model for file upload requests"""
    file_type: FileType

class FileInDB(FileBase):
    """File model as stored in database"""
    id: UUID
    user_id: UUID
    file_type: FileType
    file_path: str  # Supabase storage path
    file_url: str   # Public URL for the file
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    original_filename: str
    created_at: datetime
    updated_at: datetime

class FileResponse(FileBase):
    """File model for API responses"""
    id: UUID
    user_id: UUID
    file_type: FileType
    file_url: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    original_filename: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LinkBase(BaseModel):
    """Base link model with common fields"""
    title: str
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    is_public: bool = False

class LinkCreate(LinkBase):
    """Model for link creation requests"""
    url: HttpUrl
    link_type: Optional[LinkType] = None

class LinkInDB(LinkBase):
    """Link model as stored in database"""
    id: UUID
    user_id: UUID
    url: str
    link_type: LinkType
    created_at: datetime
    updated_at: datetime

class LinkResponse(LinkBase):
    """Link model for API responses"""
    id: UUID
    user_id: UUID
    url: str
    link_type: LinkType
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FileListResponse(BaseModel):
    """Response model for file list"""
    files: list[FileResponse]
    total: int
    page: int
    per_page: int

class LinkListResponse(BaseModel):
    """Response model for link list"""
    links: list[LinkResponse]
    total: int
    page: int
    per_page: int 