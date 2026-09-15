"""
routers/video.py
-----------------
Video Upload, Validation, Storage, History aur Processing Status APIs.
Yeh sab Module 1 document ke section 12 (Video Upload) aur uske baad
wale sections ka implementation hai.
"""

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Video, VideoStatus
from app.schemas import VideoOut, VideoUploadResponse
from app.config import UPLOAD_DIR, MAX_UPLOAD_SIZE_BYTES, ALLOWED_VIDEO_EXTENSIONS
from app.ffmpeg_utils import process_video

router = APIRouter(prefix="/api/videos", tags=["Videos"])

Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


def run_ffmpeg_pipeline(video_id: str, file_path: str, db_url: str):
    """
    Background task: upload ke baad chalta hai taki user ko turant
    response mil jaaye aur processing background mein ho.

    NOTE: Simplicity ke liye yeh apna khud ka DB session banata hai
    (background task mein request wala session use nahi karna chahiye).
    """
    from app.database import SessionLocal  # local import to avoid circular issues

    db = SessionLocal()
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            return

        video.status = VideoStatus.PROCESSING
        db.commit()

        thumbnail_path = str(Path(UPLOAD_DIR) / "thumbnails" / f"{video_id}.jpg")
        result = process_video(file_path, thumbnail_path)

        if result["success"]:
            video.duration_seconds = result["duration_seconds"]
            video.status = VideoStatus.COMPLETED
        else:
            video.status = VideoStatus.FAILED

        db.commit()
    finally:
        db.close()


@router.post("/upload", response_model=VideoUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Video upload karta hai. Steps:
    1. File extension validate karo (sirf video formats allowed)
    2. File size validate karo (max limit se zyada na ho)
    3. Disk par save karo (unique filename ke saath, taki clash na ho)
    4. Database mein record banao (status = UPLOADED)
    5. Background mein FFmpeg pipeline start karo
    """
    # 1. Extension validation
    original_filename = file.filename or "unknown"
    extension = Path(original_filename).suffix.lower()
    if extension not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{extension}'. Allowed types: {sorted(ALLOWED_VIDEO_EXTENSIONS)}",
        )

    # 2. Read file content and validate size
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max allowed size is {MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB.",
        )
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # 3. Save to disk with a unique name (avoid overwriting other users' files)
    unique_name = f"{uuid.uuid4()}{extension}"
    save_path = Path(UPLOAD_DIR) / unique_name
    with open(save_path, "wb") as f:
        f.write(content)

    # 4. Create DB record, linked to the logged-in user
    video = Video(
        user_id=current_user.id,
        filename=original_filename,
        file_path=str(save_path),
        status=VideoStatus.UPLOADED,
    )
    db.add(video)
    db.commit()
    db.refresh(video)

    # 5. Kick off FFmpeg processing in the background (non-blocking)
    background_tasks.add_task(run_ffmpeg_pipeline, video.id, str(save_path), None)

    return VideoUploadResponse(
        message="Video uploaded successfully. Processing has started in the background.",
        video=video,
    )


@router.get("/history", response_model=list[VideoOut])
def upload_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Logged-in user ke saare uploads, sabse naye pehle."""
    videos = (
        db.query(Video)
        .filter(Video.user_id == current_user.id)
        .order_by(Video.uploaded_at.desc())
        .all()
    )
    return videos


@router.get("/{video_id}/status", response_model=VideoOut)
def get_video_status(
    video_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Ek specific video ka processing status check karta hai (polling ke liye)."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found.")
    if video.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have access to this video.")
    return video
