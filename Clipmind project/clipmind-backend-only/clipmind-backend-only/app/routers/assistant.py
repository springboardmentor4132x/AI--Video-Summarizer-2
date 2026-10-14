
 
"""
routers/assistant.py
----------------------
Module 4 (extra feature): AI Assistant chat box ka API endpoint.
 
Yeh transcript, summary aur key-moments data ko context ki tarah use
karke user ke sawaal ka jawab deta hai (app/assistant_utils.py mein
poori free/local logic hai — koi paid AI API call nahi hoti).
"""
 
import json
 
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
 
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Video, Transcript, Topic, KeyMoment, KeyMomentStatus
from app.transcript_utils import generate_summary
from app.assistant_utils import answer_question
 
router = APIRouter(prefix="/api/videos", tags=["Assistant"])
 
 
class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)
 
 
@router.post("/{video_id}/assistant/ask")
def ask_assistant(
    video_id: str,
    payload: AskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """User ka sawal leta hai aur video ke transcript/summary/keymoments
    data ke basis par local logic se jawab deta hai."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or video.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Video not found.")
 
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question khaali nahi ho sakta.")
 
    # ---------- Transcript context ----------
    transcript_row = db.query(Transcript).filter(Transcript.video_id == video_id).first()
    if transcript_row:
        segments = json.loads(transcript_row.segments_json) if transcript_row.segments_json else []
        transcript_ctx = {
            "status": transcript_row.status,
            "full_text": transcript_row.full_text,
            "segments": segments,
        }
    else:
        segments = []
        transcript_ctx = {"status": "NOT_STARTED", "full_text": None, "segments": []}
 
    # ---------- Summary context (on-the-fly, jaise /summary endpoint karta hai) ----------
    if transcript_row and transcript_row.status == "COMPLETED":
        summary_data = generate_summary(transcript_row.full_text or "", segments)
        summary_ctx = {"status": "COMPLETED", **summary_data}
    else:
        summary_ctx = {
            "status": transcript_row.status if transcript_row else "NOT_STARTED",
            "short_summary": None,
            "topics": [],
        }
 
    # ---------- Key moments context ----------
    km_status_row = db.query(KeyMomentStatus).filter(KeyMomentStatus.video_id == video_id).first()
    topics_rows = db.query(Topic).filter(Topic.video_id == video_id).order_by(Topic.start_time).all()
    moments_rows = db.query(KeyMoment).filter(KeyMoment.video_id == video_id).order_by(KeyMoment.start_time).all()
 
    keymoments_ctx = {
        "status": km_status_row.status if km_status_row else "NOT_STARTED",
        "topics": [
            {"title": t.title, "start_time": t.start_time, "end_time": t.end_time} for t in topics_rows
        ],
        "key_moments": [
            {
                "start_time": m.start_time,
                "end_time": m.end_time,
                "text": m.text,
                "score": float(m.importance_score),
            }
            for m in moments_rows
        ],
    }
 
    context = {
        "video": {
            "filename": video.filename,
            "duration_seconds": video.duration_seconds,
            "status": video.status.value if hasattr(video.status, "value") else video.status,
        },
        "transcript": transcript_ctx,
        "summary": summary_ctx,
        "keymoments": keymoments_ctx,
    }
 
    result = answer_question(payload.question, context)
    return result
