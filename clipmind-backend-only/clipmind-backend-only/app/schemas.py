"""
schemas.py
----------
Pydantic models — ye define karte hain ki API request/response mein
data kaisa dikhna chahiye (validation ke liye).
"""

import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from app.models import UserRole, VideoStatus


# ---------- User / Auth schemas ----------

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)
    role: UserRole


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: UserRole
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Video schemas ----------

class VideoOut(BaseModel):
    id: str
    filename: str
    status: VideoStatus
    duration_seconds: Optional[int] = None
    uploaded_at: datetime.datetime

    class Config:
        from_attributes = True


class VideoUploadResponse(BaseModel):
    message: str
    video: VideoOut
