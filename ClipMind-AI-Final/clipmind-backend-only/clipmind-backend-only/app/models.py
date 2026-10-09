"""
models.py
---------
Database tables define karta hai: User aur Video.
Yeh Module 1 document ke "Database Design" section se match karta hai.
"""

import os
import enum
import uuid
import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class UserRole(str, enum.Enum):
    """4 roles jo document mein bataye gaye hain."""
    CONTENT_CREATOR = "content_creator"
    LEARNER = "learner"
    EDUCATOR = "educator"
    ADMIN = "administrator"


class VideoStatus(str, enum.Enum):
    """Video processing ka lifecycle."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # yeh hashed password store karta hai, plain text kabhi nahi
    role = Column(Enum(UserRole), nullable=False, default=UserRole.LEARNER)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    videos = relationship("Video", back_populates="owner", cascade="all, delete-orphan")


class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    status = Column(Enum(VideoStatus), nullable=False, default=VideoStatus.UPLOADED)
    duration_seconds = Column(Integer, nullable=True)   # FFmpeg se nikala jaayega
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="videos")

    @property
    def video_file(self):
        """file_path se sirf asli filename nikalta hai (jo disk pe UPLOAD_DIR mein saved hai)."""
        return os.path.basename(self.file_path)


# --- Module 3: Key Moments Detection ke liye naye tables ---

class Transcript(Base):
    """
    segments_json format: [{"start": 0, "end": 15, "text": "..."}, ...]
    status: NOT_STARTED/PROCESSING/COMPLETED/FAILED
    """
    __tablename__ = "transcripts"

    id = Column(String, primary_key=True, default=generate_uuid)
    video_id = Column(String, ForeignKey("videos.id"), nullable=False, unique=True)
    full_text = Column(String, nullable=True)
    segments_json = Column(String, nullable=False)  # JSON string as text
    status = Column(String, nullable=False, default="completed")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Topic(Base):
    __tablename__ = "topics"

    id = Column(String, primary_key=True, default=generate_uuid)
    video_id = Column(String, ForeignKey("videos.id"), nullable=False)
    title = Column(String, nullable=False)
    start_time = Column(Integer, nullable=False)  # seconds
    end_time = Column(Integer, nullable=False)


class KeyMoment(Base):
    __tablename__ = "key_moments"

    id = Column(String, primary_key=True, default=generate_uuid)
    video_id = Column(String, ForeignKey("videos.id"), nullable=False)
    topic_title = Column(String, nullable=True)
    start_time = Column(Integer, nullable=False)   # seconds
    end_time = Column(Integer, nullable=False)
    text = Column(String, nullable=False)
    importance_score = Column(String, nullable=False)  # store as string "0.86" (SQLite float precision safe)


class KeyMomentStatus(Base):
    __tablename__ = "key_moment_status"

    video_id = Column(String, ForeignKey("videos.id"), primary_key=True)
    status = Column(String, nullable=False, default="NOT_STARTED")  # NOT_STARTED/PROCESSING/COMPLETED/FAILED
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)