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
    extension_clean = extension.lstrip(".")
    video = Video(
        user_id=current_user.id,
        filename=safe_filename,
        file_path=str(file_path),
        file_type=extension_clean,
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


from app.database import SessionLocal
from app.services.ai_service import generate_video_summary
from app.services.embedding_service import process_and_store_embeddings
from fastapi import BackgroundTasks

def process_video_pipeline_background(video_id: int, file_path: str, filename: str, file_type: str, user_id: int):
    """Heavy background worker for transcribing and embedding videos natively."""
    bg_db = SessionLocal()
    try:
        video = bg_db.query(Video).filter(Video.id == video_id).first()
        if not video:
            return

        print(f"\n[Worker] Starting dedicated background AI pipeline for Video {video_id}...")
        
        # 1. Run Heavy AI Transcript & Summary Module (Whisper & HF)
        summary_data = generate_video_summary(file_path, filename, file_type)
        
        video.summary = summary_data["summary"]
        video.transcript = summary_data.get("transcript", "Transcript unavailable.")
        video.status = "completed"
        bg_db.commit()
        
        # 2. Offload semantic chunking and native ARRAY(Float) embedding
        process_and_store_embeddings(video.transcript, video_id, user_id, bg_db)
        print(f"[Worker] Pipeline complete! Successfully finished processing Video {video_id}")

    except Exception as e:
        bg_db.rollback()
        video = bg_db.query(Video).filter(Video.id == video_id).first()
        if video:
            video.status = "failed"
            bg_db.commit()
        print(f"[Worker] Fatal Background Processing Error: {e}")
    finally:
        bg_db.close()

@router.get("/{video_id}/summary")
def get_video_summary(
    video_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Triggers AI summary processing in the background, keeping the API fast and non-blocking.
    """
    video = (
        db.query(Video)
        .filter(Video.id == video_id, Video.user_id == current_user.id)
        .first()
    )

    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

    # If it is currently being crushed by the Background Worker
    if video.status == "processing":
        return {
            "video_id": video.id,
            "filename": video.filename,
            "status": "processing",
            "message": "AI is actively analyzing this video in the background. Please wait...",
            "summary": "Processing...",
            "takeaways": [],
            "transcript": "Processing..."
        }

    # Check if summary & transcript are already safely finished and cached
    if video.status == "completed" and video.summary:
        return {
            "video_id": video.id,
            "filename": video.filename,
            "summary": video.summary,
            "takeaways": [
                "Persisted directly from PostgreSQL.",
                "Zero background worker usage consumed.",
                "Automated database caching activated."
            ],
            "transcript": video.transcript,
        }

    # Lock the video state to prevent duplicate requests from firing
    video.status = "processing"
    db.commit()
    
    # Hand the heavy CPU AI task to FastAPI's Background Worker Queue!
    background_tasks.add_task(
        process_video_pipeline_background, 
        video.id, 
        video.file_path, 
        video.filename, 
        video.file_type or "mp4", 
        current_user.id
    )

    return {
        "video_id": video.id,
        "filename": video.filename,
        "status": "processing",
        "message": "Video sent to Dedicated AI Background Worker! UI will not freeze.",
        "summary": "Processing...",
        "takeaways": [],
        "transcript": "Processing..."
    }