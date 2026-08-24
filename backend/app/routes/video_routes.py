"""
video_routes.py
---------------
API endpoints for video management.

POST   /videos/upload       -> Upload/register a video
GET    /videos              -> Get current user's videos
GET    /videos/{video_id}  -> Get one video
DELETE /videos/{video_id}  -> Delete a video
"""

import os
import shutil
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    status,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Video, User
from app.auth import get_current_user


router = APIRouter(
    prefix="/videos",
    tags=["Videos"]
)


# Directory where uploaded videos will be stored
UPLOAD_DIR = Path("uploads/videos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
def upload_video(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a video for the currently authenticated user.
    """

    # Basic video-file validation
    allowed_extensions = {
        ".mp4",
        ".avi",
        ".mov",
        ".mkv",
        ".webm",
    }

    extension = Path(file.filename).suffix.lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported video format",
        )

    # Create a user-specific directory
    user_dir = UPLOAD_DIR / str(current_user.id)
    user_dir.mkdir(parents=True, exist_ok=True)

    # Avoid directly trusting the uploaded filename
    safe_filename = Path(file.filename).name
    file_path = user_dir / safe_filename

    # Save uploaded file
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    # Save metadata in PostgreSQL
    video = Video(
        user_id=current_user.id,
        filename=safe_filename,
        file_path=str(file_path),
        status="uploaded",
    )

    db.add(video)
    db.commit()
    db.refresh(video)

    return {
        "id": video.id,
        "filename": video.filename,
        "file_path": video.file_path,
        "status": video.status,
        "uploaded_at": video.uploaded_at,
        "message": "Video uploaded successfully",
    }


@router.get("/")
def get_my_videos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return all videos belonging to the authenticated user.
    """

    videos = (
        db.query(Video)
        .filter(Video.user_id == current_user.id)
        .order_by(Video.uploaded_at.desc())
        .all()
    )

    return videos


@router.get("/{video_id}")
def get_video(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return one video belonging to the authenticated user.
    """

    video = (
        db.query(Video)
        .filter(
            Video.id == video_id,
            Video.user_id == current_user.id,
        )
        .first()
    )

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )

    return video


@router.delete("/{video_id}")
def delete_video(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a video belonging to the authenticated user.
    """

    video = (
        db.query(Video)
        .filter(
            Video.id == video_id,
            Video.user_id == current_user.id,
        )
        .first()
    )

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )

    # Delete physical file
    if os.path.exists(video.file_path):
        os.remove(video.file_path)

    # Delete database record
    db.delete(video)
    db.commit()

    return {
        "message": "Video deleted successfully",
        "video_id": video_id,
    }