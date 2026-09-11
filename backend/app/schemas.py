"""
schemas.py
-----------
Pydantic models used to validate incoming request data and shape outgoing
response data. These are separate from models.py (SQLAlchemy) on purpose:
- models.py   -> how data is stored in PostgreSQL
- schemas.py  -> how data looks going in/out of the API
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from enum import Enum


class RoleEnum(str, Enum):
    content_creator = "content_creator"
    learner = "learner"
    educator = "educator"
    administrator = "administrator"


# ---- Incoming (request) schemas ----

class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, description="Plain text password, hashed before storage")
    role: RoleEnum


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ---- Outgoing (response) schemas ----

class UserOut(BaseModel):
    id: str | int  # UI expects string or int gracefully
    full_name: str = Field(validation_alias='name')
    email: EmailStr
    role: RoleEnum
    created_at: datetime
    bio: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True
        populate_by_name = True


class VideoOut(BaseModel):
    id: str | int
    owner_id: str | int = Field(validation_alias="user_id")
    owner_name: Optional[str] = None
    original_filename: str = Field(validation_alias="filename")
    title: str = Field(..., validation_alias="filename")
    description: Optional[str] = None
    status: str
    is_public: bool = False
    duration: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: Optional[int] = None
    error_message: Optional[str] = None
    has_thumbnail: bool = False
    has_audio: bool = True
    created_at: datetime = Field(validation_alias="uploaded_at")
    
    # Internal DB fields passed strictly for API stability
    file_path: Optional[str] = None
    file_type: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"