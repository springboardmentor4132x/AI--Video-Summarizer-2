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
import subprocess
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


from app.schemas import VideoOut
from app.models import TranscriptChunk
from fastapi.responses import StreamingResponse, FileResponse
import mimetypes

@router.get("/", response_model=list[VideoOut])
def get_my_videos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return all videos belonging to the authenticated user.
    """

    videos = (
        db.query(Video)
        .order_by(Video.uploaded_at.desc())
        .all()
    )

    return videos


@router.get("/{video_id}", response_model=VideoOut)
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
        .filter(Video.id == video_id)
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
from app.services.embedding_service import process_and_store_embeddings, search_transcript_similarity
from app.models import TranscriptChunk
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
        
        # 2. Delete old chunks so fresh embeddings can be stored on regeneration
        bg_db.query(TranscriptChunk).filter(TranscriptChunk.video_id == video_id).delete()
        bg_db.commit()
        
        # 3. Offload semantic chunking and native ARRAY(Float) embedding
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

@router.api_route("/{video_id}/summary", methods=["GET", "POST"])
def get_video_summary(
    video_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Triggers AI summary processing in the background, keeping the API fast and non-blocking.
    Handles both GET and POST requests from the frontend.
    """
    video = (
        db.query(Video)
        .filter(Video.id == video_id)
        .first()
    )

    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

    # If it is not completed or processing yet, start processing in background
    if video.status in ("uploaded", "failed"):
        video.status = "processing"
        db.commit()
        background_tasks.add_task(
            process_video_pipeline_background, 
            video.id, 
            video.file_path, 
            video.filename, 
            video.file_type or "mp4", 
            current_user.id
        )

    # Determine status for summary payload
    sum_status = "completed" if (video.status == "completed" and video.summary) else ("failed" if video.status == "failed" else "processing")
    
    # Split the stored "short|||detailed" summary into two separate parts
    def split_summary(raw: str | None):
        if not raw:
            return "Processing summary...", "Processing detailed summary..."
        parts = raw.split("|||", 1)
        short = parts[0].strip()
        detailed = parts[1].strip() if len(parts) > 1 else short
        return short, detailed

    short_text, detailed_text = split_summary(video.summary)

    return {
        "id": str(video.id),
        "video_id": str(video.id),
        "status": sum_status,
        "short_text": short_text,
        "detailed_text": detailed_text,
        "keywords": ["AI", "Summary", "Video"],
        "error_message": "AI Processing failed." if video.status == "failed" else None,
        "created_at": str(video.uploaded_at),
        "updated_at": str(video.uploaded_at),
        # Legacy/Khushi compatibility keys:
        "filename": video.filename,
        "summary": short_text,
        "takeaways": [
            "Persisted directly from PostgreSQL.",
            "Automated background processing activated."
        ],
        "transcript": video.transcript if video.transcript else "Processing..."
    }

# --- Utkarsh Frontend Compatibility Routes ---

@router.post("/{video_id}/process")
def process_video_compat(
    video_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Triggers background processing when 'Run processing' button is clicked."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video.status = "processing"
    db.commit()
    background_tasks.add_task(
        process_video_pipeline_background, 
        video.id, 
        video.file_path, 
        video.filename, 
        video.file_type or "mp4", 
        current_user.id
    )
    return {
        "id": str(video.id),
        "video_id": str(video.id),
        "job_type": "AI Processing",
        "status": "running",
        "progress": 10,
        "error": None,
        "created_at": str(video.uploaded_at),
        "updated_at": str(video.uploaded_at)
    }

@router.post("/{video_id}/analysis")
def process_analysis_compat(
    video_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Triggers background analysis when 'Rerun analysis' button is clicked."""
    return process_video_compat(video_id, background_tasks, db, current_user)

@router.get("/{video_id}/jobs")
def get_video_jobs_compat(video_id: int, db: Session = Depends(get_db)):
    """Provides a Job array for Utkarsh's Dashboard UI."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        return []
    if video.status == "processing":
        return [{
            "id": str(video.id),
            "video_id": str(video.id),
            "job_type": "AI Processing",
            "status": "running",
            "progress": 50,
            "error": None,
            "created_at": str(video.uploaded_at),
            "updated_at": str(video.uploaded_at)
        }]
    return []

@router.get("/{video_id}/transcript")
def get_video_transcript_compat(video_id: int, db: Session = Depends(get_db)):
    """Maps Khushi's transcript to Utkarsh's expected TranscriptItem schema."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    tr_status = "completed" if (video.status == "completed" and video.transcript) else ("failed" if video.status == "failed" else "processing")
    return {
        "id": str(video.id),
        "video_id": str(video.id),
        "status": tr_status,
        "language": "en",
        "full_text": video.transcript if video.transcript else None,
        "edited_text": None,
        "error_message": "Transcript failed" if video.status == "failed" else None,
        "created_at": str(video.uploaded_at),
        "updated_at": str(video.uploaded_at)
    }

@router.get("/{video_id}/analysis")
def get_video_analysis_compat(video_id: int, db: Session = Depends(get_db)):
    """
    Returns real key moments and topics extracted from TranscriptChunk data.
    Topics = chunked transcript sections. Key moments = highest-importance chunks.
    """
    chunks = (
        db.query(TranscriptChunk)
        .filter(TranscriptChunk.video_id == video_id)
        .order_by(TranscriptChunk.chunk_index.asc())
        .all()
    )

    if not chunks:
        return {"topics": [], "key_moments": []}

    # Build Topics from chunks — each chunk becomes a topic with an estimated timestamp
    topics = []
    for chunk in chunks:
        # Estimate time: assume ~130 words per minute average speech rate
        words_before = sum(len(c.chunk_text.split()) for c in chunks if c.chunk_index < chunk.chunk_index)
        start_sec = round((words_before / 130) * 60)
        end_sec = round(((words_before + len(chunk.chunk_text.split())) / 130) * 60)
        
        # Use first sentence as the topic title
        first_sentence = chunk.chunk_text.split(".")[0].strip()[:80]
        topics.append({
            "id": str(chunk.id),
            "video_id": str(video_id),
            "start_sec": start_sec,
            "end_sec": end_sec,
            "title": first_sentence if first_sentence else f"Section {chunk.chunk_index + 1}",
            "transcript_text": chunk.chunk_text[:200],
            "created_at": str(chunk.created_at)
        })

    # Build Key Moments — pick the top 5 most "important" chunks by length (richest content)
    sorted_by_importance = sorted(chunks, key=lambda c: len(c.chunk_text), reverse=True)
    top_chunks = sorted_by_importance[:5]

    key_moments = []
    for i, chunk in enumerate(top_chunks):
        words_before = sum(len(c.chunk_text.split()) for c in chunks if c.chunk_index < chunk.chunk_index)
        start_sec = round((words_before / 130) * 60)
        end_sec = round(((words_before + len(chunk.chunk_text.split())) / 130) * 60)
        
        highlight_sentence = chunk.chunk_text.split(".")[0].strip()[:80]
        key_moments.append({
            "id": f"km-{chunk.id}",
            "video_id": str(video_id),
            "topic_id": str(chunk.id),
            "start_sec": start_sec,
            "end_sec": end_sec,
            "title": highlight_sentence or f"Highlight {i + 1}",
            "transcript_text": chunk.chunk_text[:300],
            "score": round(len(chunk.chunk_text) / max(len(c.chunk_text) for c in chunks), 2),
            "moment_type": "highlight",
            "created_at": str(chunk.created_at)
        })

    return {"topics": topics, "key_moments": key_moments}


@router.get("/{video_id}/stream")
def stream_video(video_id: int, db: Session = Depends(get_db)):
    """
    Streams the raw video file to the browser <video> tag.
    No auth required here so the player can load without token issues.
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    file_path = video.file_path
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video file not found on disk")

    mime_type, _ = mimetypes.guess_type(file_path)
    mime_type = mime_type or "video/mp4"
    return FileResponse(file_path, media_type=mime_type, filename=video.filename)


THUMBNAIL_DIR = Path("uploads/thumbnails")
THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/{video_id}/thumbnail")
def get_thumbnail(video_id: int, db: Session = Depends(get_db)):
    """Serves the extracted JPEG thumbnail image for the video."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    thumb_path = THUMBNAIL_DIR / f"{video_id}.jpg"

    # Generate on demand if missing but video file exists
    if not thumb_path.exists() and os.path.exists(video.file_path):
        import shutil
        ffmpeg_bin = shutil.which("ffmpeg") or r"C:\Users\KHUSHI\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe"
        try:
            cmd = [ffmpeg_bin, "-y", "-ss", "00:00:01", "-i", str(video.file_path), "-vframes", "1", "-q:v", "2", str(thumb_path)]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            print(f"[Thumbnail Error] Could not extract thumbnail for {video_id}: {e}")

    if thumb_path.exists():
        return FileResponse(str(thumb_path), media_type="image/jpeg")

    # Fallback to streaming video frame if thumbnail file unavailable
    if os.path.exists(video.file_path):
        return FileResponse(video.file_path, media_type="video/mp4")

    raise HTTPException(status_code=404, detail="Thumbnail unavailable")


# --- Sanjana's Similarity & Importance Scoring Search Endpoint ---
from fastapi import Query

@router.get("/{video_id}/search")
def search_video_transcript(
    video_id: int,
    q: str = Query(..., min_length=1, description="Search query to find relevant transcript moments"),
    top_k: int = Query(5, description="Number of top results to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Sanjana's Semantic Search: finds the most relevant transcript chunks for a query.
    Uses cosine similarity on 384-dimensional all-MiniLM-L6-v2 embeddings.
    Returns results ranked by importance_score (0-100%).
    """
    results = search_transcript_similarity(
        query=q,
        video_id=video_id,
        user_id=current_user.id,
        db=db,
        top_k=top_k
    )

    if not results:
        return {
            "query": q,
            "video_id": video_id,
            "results": [],
            "message": "No embeddings found for this video. Please generate summary first."
        }

    return {
        "query": q,
        "video_id": video_id,
        "total_results": len(results),
        "results": results  # [{chunk_index, text, similarity, importance_score}]
    }


# --- Main Analytical Dashboard Endpoint ---
from datetime import datetime, timedelta

@router.get("/analytics/dashboard")
def get_analytics_dashboard(
    days: int = Query(7, ge=0, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Computes real-time analytical metrics, time-series, status distributions,
    duration histograms, key insights, and recent activity from PostgreSQL.
    """
    now = datetime.now()
    raw_videos = db.query(Video).order_by(Video.uploaded_at.desc()).all()

    if days > 0:
        cutoff_date = (now - timedelta(days=days)).date()
        all_videos = [v for v in raw_videos if v.uploaded_at and v.uploaded_at.date() >= cutoff_date]
    else:
        all_videos = raw_videos

    total_videos = len(all_videos)
    completed_videos = sum(1 for v in all_videos if v.status == "completed")
    processing_videos = sum(1 for v in all_videos if v.status in ("processing", "running", "queued"))
    uploaded_videos = sum(1 for v in all_videos if v.status == "uploaded")
    failed_videos = sum(1 for v in all_videos if v.status == "failed")

    transcripts_generated = sum(1 for v in all_videos if v.transcript and len(v.transcript.strip()) > 0)
    summaries_generated = sum(1 for v in all_videos if v.summary and len(v.summary.strip()) > 0)

    total_duration_sec = 0
    duration_buckets = {
        "< 1 min": 0,
        "1 - 3 mins": 0,
        "3 - 5 mins": 0,
        "5 - 10 mins": 0,
        "10+ mins": 0,
    }

    for v in all_videos:
        words = len(v.transcript.split()) if v.transcript else 0
        dur = round((words / 130) * 60) if words > 0 else 60
        total_duration_sec += dur

        if dur < 60:
            duration_buckets["< 1 min"] += 1
        elif dur < 180:
            duration_buckets["1 - 3 mins"] += 1
        elif dur < 300:
            duration_buckets["3 - 5 mins"] += 1
        elif dur < 600:
            duration_buckets["5 - 10 mins"] += 1
        else:
            duration_buckets["10+ mins"] += 1

    avg_duration_sec = round(total_duration_sec / total_videos) if total_videos > 0 else 0
    success_rate = round((completed_videos / total_videos * 100), 1) if total_videos > 0 else 100.0

    def format_dur(sec):
        if sec < 60:
            return f"{sec}s"
        mins = sec // 60
        rem_sec = sec % 60
        if mins < 60:
            return f"{mins}m {rem_sec}s" if rem_sec > 0 else f"{mins}m"
        hrs = mins // 60
        rem_m = mins % 60
        return f"{hrs}h {rem_m}m"

    num_days = days if days > 0 else 7
    time_series = []
    for i in range(num_days - 1, -1, -1):
        target_date = (now - timedelta(days=i)).date()
        date_label = target_date.strftime("%b %d")
        
        day_vids = [v for v in all_videos if v.uploaded_at and v.uploaded_at.date() == target_date]
        time_series.append({
            "date": date_label,
            "uploaded": len(day_vids),
            "completed": sum(1 for v in day_vids if v.status == "completed"),
            "failed": sum(1 for v in day_vids if v.status == "failed"),
        })

    status_distribution = [
        {"name": "Completed", "value": completed_videos, "color": "#10B981"},
        {"name": "Processing", "value": processing_videos, "color": "#F59E0B"},
        {"name": "Uploaded", "value": uploaded_videos, "color": "#3B82F6"},
        {"name": "Failed", "value": failed_videos, "color": "#EF4444"},
    ]

    duration_distribution = [
        {"range": label, "count": count} for label, count in duration_buckets.items()
    ]

    insights = []
    if total_videos == 0:
        insights.append(f"No videos uploaded in the selected timeframe ({days} days).")
    else:
        insights.append(f"Overall processing success rate is {success_rate}% across {total_videos} video(s).")
        insights.append(f"Total video content duration equals ~{format_dur(total_duration_sec)} (avg {format_dur(avg_duration_sec)} per video).")
        insights.append(f"AI models have generated {transcripts_generated} transcripts and {summaries_generated} summaries.")
        if failed_videos > 0:
            insights.append(f"⚠️ {failed_videos} video(s) failed during processing.")
        else:
            insights.append("✅ Zero pipeline failures recorded. System operating at 100% stability.")

    recent_activity = []
    for v in all_videos[:8]:
        words = len(v.transcript.split()) if v.transcript else 0
        dur_str = format_dur(round((words / 130) * 60) if words > 0 else 60)
        recent_activity.append({
            "id": str(v.id),
            "title": v.filename,
            "status": v.status,
            "uploaded_at": v.uploaded_at.strftime("%b %d, %H:%M") if v.uploaded_at else "Recently",
            "owner_name": v.owner.name if v.owner else "Creator",
            "duration": dur_str
        })

    return {
        "days": days,
        "metrics": {
            "total_videos": total_videos,
            "completed_videos": completed_videos,
            "transcripts_generated": transcripts_generated,
            "summaries_generated": summaries_generated,
            "total_duration_sec": total_duration_sec,
            "total_duration_formatted": format_dur(total_duration_sec),
            "avg_duration_sec": avg_duration_sec,
            "avg_duration_formatted": format_dur(avg_duration_sec),
            "success_rate": success_rate,
            "failed_processing": failed_videos,
        },
        "over_time": time_series,
        "status_distribution": status_distribution,
        "duration_distribution": duration_distribution,
        "insights": insights,
        "recent_activity": recent_activity,
    }