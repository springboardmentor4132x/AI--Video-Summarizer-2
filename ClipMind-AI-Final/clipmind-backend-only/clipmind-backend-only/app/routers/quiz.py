
"""
routers/quiz.py
-----------------
Self-assessment feature: video ke transcript se MCQ quiz generate karta hai
(100% free/local, Module 2 ke summary topics par based).
"""
 
import json
 
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
 
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Video, Transcript
from app.transcript_utils import generate_summary
from app.quiz_utils import generate_quiz
 
router = APIRouter(prefix="/api/videos", tags=["Quiz"])
 
 
@router.get("/{video_id}/quiz")
def get_quiz(
    video_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Video ke transcript/topics se MCQ self-assessment questions banata hai."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or video.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Video not found.")
 
    transcript = db.query(Transcript).filter(Transcript.video_id == video_id).first()
    if not transcript or transcript.status != "COMPLETED":
        raise HTTPException(
            status_code=400,
            detail="Transcript abhi complete nahi hua — pehle Transcript page se generate karein.",
        )
 
    segments = json.loads(transcript.segments_json) if transcript.segments_json else []
    summary = generate_summary(transcript.full_text or "", segments)
    topics = summary.get("topics", [])
 
    questions = generate_quiz(transcript.full_text or "", topics, num_questions=5)
    if not questions:
        raise HTTPException(
            status_code=400,
            detail="Is video se quiz banane ke liye kaafi content nahi mila (video bahut chhota ho sakta hai).",
        )
 
    return {"questions": questions}
