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
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, description="Plain text password, hashed before storage")
    role: RoleEnum


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ---- Outgoing (response) schemas ----

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: RoleEnum
    created_at: datetime

    class Config:
        from_attributes = True  # allows creating this from a SQLAlchemy User object


class VideoOut(BaseModel):
    id: int
    user_id: int
    filename: str
    file_path: str
    file_type: Optional[str] = None
    status: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"