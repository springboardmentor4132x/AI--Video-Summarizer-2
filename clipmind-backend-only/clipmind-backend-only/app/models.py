"""
models.py
---------
Database tables define karta hai: User aur Video.
Yeh Module 1 document ke "Database Design" section se match karta hai.
"""

import enum
import uuid
import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class UserRole(str, enum.Enum):
    CONTENT_CREATOR = "content_creator"
    LEARNER = "learner"
    EDUCATOR = "educator"
    ADMIN = "administrator"


class VideoStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TranscriptStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SummaryStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
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
    duration_seconds = Column(Integer, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="videos")
    transcript = relationship(
        "Transcript", back_populates="video", uselist=False, cascade="all, delete-orphan"
    )


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(String, primary_key=True, default=generate_uuid)
    video_id = Column(String, ForeignKey("videos.id"), unique=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    transcript_text = Column(String, nullable=True)
    status = Column(Enum(TranscriptStatus), nullable=False, default=TranscriptStatus.NOT_STARTED)
    error_message = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    video = relationship("Video", back_populates="transcript")
    summary = relationship(
        "Summary", back_populates="transcript", uselist=False, cascade="all, delete-orphan"
    )


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(String, primary_key=True, default=generate_uuid)
    transcript_id = Column(String, ForeignKey("transcripts.id"), unique=True, nullable=False)
    video_id = Column(String, ForeignKey("videos.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    short_summary = Column(String, nullable=True)
    detailed_summary = Column(String, nullable=True)
    status = Column(Enum(SummaryStatus), nullable=False, default=SummaryStatus.NOT_STARTED)
    error_message = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    transcript = relationship("Transcript", back_populates="summary")