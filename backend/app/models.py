"""
models.py
---------
SQLAlchemy ORM models defining the database schema for ClipMind AI.

Entities:
- User : Stored user accounts with hashed passwords and role-based permissions.
- Video: Metadata for videos uploaded by users for processing.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    """
    User entity representing system users across 4 primary roles:
    - content_creator
    - learner
    - educator
    - administrator
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="learner")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship to uploaded videos
    videos = relationship("Video", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"


class Video(Base):
    """
    Video entity representing uploaded videos and their processing status.
    """
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=True)  # e.g., mp4, webm, mov, mkv
    status = Column(String(50), nullable=False, default="uploaded")  # e.g., uploaded, processing, completed, failed
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship to owning user
    owner = relationship("User", back_populates="videos")

    def __repr__(self):
        return f"<Video(id={self.id}, filename='{self.filename}', status='{self.status}')>"
