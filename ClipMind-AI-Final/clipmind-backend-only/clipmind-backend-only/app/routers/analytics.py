
"""
routers/analytics.py
----------------------
Milestone 3: Analytics feature.
 
User ke sabhi videos ka ek overall overview (total videos, duration,
status breakdown, transcripts/topics/key-moments count) aur har video ka
alag-alag insight (word count, topics count, key moments count) deta hai.
"""
 
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
 
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Video, VideoStatus, Transcript, Topic, KeyMoment
 
router = APIRouter(prefix="/api/analytics", tags=["Analytics"])
 
 
def _word_count(text: str) -> int:
    return len((text or "").split())
 
 
@router.get("/overview")
def get_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """User ke sabhi videos ka overall summary — Analytics page ke top stats/graphs ke liye."""
    videos = db.query(Video).filter(Video.user_id == current_user.id).all()
    video_ids = [v.id for v in videos]
 
    total_videos = len(videos)
    total_duration_seconds = sum(v.duration_seconds or 0 for v in videos)
 
    status_breakdown = {s.value: 0 for s in VideoStatus}
    for v in videos:
        key = v.status.value if hasattr(v.status, "value") else v.status
        status_breakdown[key] = status_breakdown.get(key, 0) + 1
 
    transcripts = (
        db.query(Transcript).filter(Transcript.video_id.in_(video_ids)).all() if video_ids else []
    )
    transcripts_completed = sum(1 for t in transcripts if t.status == "COMPLETED")
    total_words_transcribed = sum(_word_count(t.full_text) for t in transcripts if t.status == "COMPLETED")
 
    total_topics_detected = (
        db.query(Topic).filter(Topic.video_id.in_(video_ids)).count() if video_ids else 0
    )
    total_key_moments_detected = (
        db.query(KeyMoment).filter(KeyMoment.video_id.in_(video_ids)).count() if video_ids else 0
    )
 
    avg_duration = round(total_duration_seconds / total_videos, 1) if total_videos else 0
 
    return {
        "total_videos": total_videos,
        "total_duration_seconds": total_duration_seconds,
        "avg_duration_seconds": avg_duration,
        "status_breakdown": status_breakdown,
        "transcripts_completed": transcripts_completed,
        "total_words_transcribed": total_words_transcribed,
        "total_topics_detected": total_topics_detected,
        "total_key_moments_detected": total_key_moments_detected,
    }
 
 
@router.get("/videos")
def get_per_video_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Har video ka alag-alag insight — Analytics page ki table/graphs ke liye."""
    videos = (
        db.query(Video)
        .filter(Video.user_id == current_user.id)
        .order_by(Video.uploaded_at.desc())
        .all()
    )
 
    insights = []
    for v in videos:
        transcript = db.query(Transcript).filter(Transcript.video_id == v.id).first()
        topics_count = db.query(Topic).filter(Topic.video_id == v.id).count()
        key_moments_count = db.query(KeyMoment).filter(KeyMoment.video_id == v.id).count()
 
        insights.append({
            "id": v.id,
            "filename": v.filename,
            "status": v.status.value if hasattr(v.status, "value") else v.status,
            "duration_seconds": v.duration_seconds or 0,
            "uploaded_at": v.uploaded_at,
            "transcript_status": transcript.status if transcript else "NOT_STARTED",
            "word_count": _word_count(transcript.full_text) if transcript and transcript.status == "COMPLETED" else 0,
            "topics_count": topics_count,
            "key_moments_count": key_moments_count,
        })
 
    return {"videos": insights}
