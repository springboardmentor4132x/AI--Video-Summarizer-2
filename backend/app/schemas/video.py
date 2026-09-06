from datetime import datetime

from pydantic import BaseModel, Field

from app.models.video import ContentStatus, JobStatus, JobType, VideoStatus


class VideoOut(BaseModel):
    id: str
    owner_id: str
    owner_name: str | None = None
    original_filename: str
    title: str
    description: str | None
    status: VideoStatus
    is_public: bool
    duration: float | None
    width: int | None
    height: int | None
    file_size: int | None
    error_message: str | None
    has_thumbnail: bool = False
    has_audio: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class VideoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=512)
    description: str | None = None
    is_public: bool | None = None


class JobOut(BaseModel):
    id: str
    video_id: str
    job_type: JobType
    status: JobStatus
    progress: int
    error: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TranscriptOut(BaseModel):
    id: str
    video_id: str
    status: ContentStatus
    language: str | None
    full_text: str | None
    edited_text: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class TranscriptUpdate(BaseModel):
    text: str = Field(min_length=1)


class SummaryOut(BaseModel):
    id: str
    video_id: str
    status: ContentStatus
    short_text: str | None
    detailed_text: str | None
    keywords: list
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class TopicOut(BaseModel):
    id: str
    video_id: str
    start_sec: float
    end_sec: float
    title: str
    transcript_text: str
    created_at: datetime


class KeyMomentOut(BaseModel):
    id: str
    video_id: str
    topic_id: str | None
    start_sec: float
    end_sec: float
    title: str
    transcript_text: str | None
    score: float | None
    moment_type: str
    created_at: datetime


class AnalysisOut(BaseModel):
    topics: list[TopicOut]
    key_moments: list[KeyMomentOut]
