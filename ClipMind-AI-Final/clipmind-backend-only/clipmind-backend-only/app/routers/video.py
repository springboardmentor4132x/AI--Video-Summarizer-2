
"""
routers/video.py
------------------
Module 1 ke core API endpoints: video upload, list, detail aur delete.
Upload hote hi FFmpeg se duration/thumbnail nikalne ka kaam background
mein chalta hai (Module 1 ke ffmpeg_utils.process_video ke through).
"""
 
import os
import uuid
from pathlib import Path
 
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, status
from sqlalchemy.orm import Session
 
from app.database import get_db, SessionLocal
from app.dependencies import get_current_user
from app.config import UPLOAD_DIR, ALLOWED_VIDEO_EXTENSIONS, MAX_UPLOAD_SIZE_BYTES
from app.models import User, Video, VideoStatus
from app.schemas import VideoOut, VideoUploadResponse
from app.ffmpeg_utils import process_video
 
router = APIRouter(prefix="/api/videos", tags=["Video"])
 
 
def run_video_processing(video_id: str, file_path: str, thumbnail_path: str):
    """Upload ke baad background mein duration/thumbnail nikalta hai."""
    db = SessionLocal()
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            return
 
        video.status = VideoStatus.PROCESSING
        db.commit()
 
        result = process_video(file_path, thumbnail_path)
 
        if result["success"]:
            video.duration_seconds = result["duration_seconds"]
            video.status = VideoStatus.COMPLETED
        else:
            video.status = VideoStatus.FAILED
 
        db.commit()
    except Exception:
        video = db.query(Video).filter(Video.id == video_id).first()
        if video:
            video.status = VideoStatus.FAILED
            db.commit()
    finally:
        db.close()
 
 
@router.post("/upload", response_model=VideoUploadResponse, status_code=status.HTTP_201_CREATED)
def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Video file upload karta hai, DB mein record banata hai, aur
    FFmpeg processing (duration/thumbnail) background mein shuru karta hai."""
 
    # ---------- Extension check ----------
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_VIDEO_EXTENSIONS))}",
        )
 
    # ---------- Save file to disk ----------
    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    unique_name = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
 
    size = 0
    with open(file_path, "wb") as out_file:
        while chunk := file.file.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_UPLOAD_SIZE_BYTES:
                out_file.close()
                os.remove(file_path)
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Max allowed size is {MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB.",
                )
            out_file.write(chunk)
 
    # ---------- DB record ----------
    video = Video(
        user_id=current_user.id,
        filename=file.filename,
        file_path=file_path,
        status=VideoStatus.UPLOADED,
    )
    db.add(video)
    db.commit()
    db.refresh(video)
 
    # ---------- Background FFmpeg processing ----------
    thumbnail_path = os.path.join(UPLOAD_DIR, f"{video.id}_thumb.jpg")
    background_tasks.add_task(run_video_processing, video.id, file_path, thumbnail_path)
 
    return VideoUploadResponse(message="Video uploaded successfully. Processing started.", video=video)
 
 
@router.get("/history", response_model=list[VideoOut])
def list_videos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Logged-in user ke sabhi uploaded videos ki list deta hai (upload history)."""
    videos = (
        db.query(Video)
        .filter(Video.user_id == current_user.id)
        .order_by(Video.uploaded_at.desc())
        .all()
    )
    return videos
 
 
@router.get("/{video_id}/status")
def get_video_status(
    video_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Video ki current processing status deta hai (upload ke baad polling ke liye)."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or video.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Video not found.")
 
    return {
        "id": video.id,
        "status": video.status.value if hasattr(video.status, "value") else video.status,
        "duration_seconds": video.duration_seconds,
        "video_file": os.path.basename(video.file_path),
    }
 
 
@router.get("/{video_id}", response_model=VideoOut)
def get_video(
    video_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Ek specific video ki detail deta hai."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or video.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Video not found.")
    return video
 
 
@router.delete("/{video_id}", status_code=status.HTTP_200_OK)
def delete_video(
    video_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Video ko DB aur disk dono se delete karta hai."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or video.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Video not found.")
 
    if os.path.exists(video.file_path):
        try:
            os.remove(video.file_path)
        except OSError:
            pass
 
    db.delete(video)
    db.commit()
    return {"message": "Video deleted successfully."}
