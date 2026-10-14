"""
routers/keymoments.py
----------------------
Module 3 ke API endpoints.
NOTE: Yeh Transcript table par depend karta hai (Module 2 se aana chahiye).
"""

"""import json

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app.dependencies import get_current_user
from app.models import User, Video, Transcript, Topic, KeyMoment, KeyMomentStatus
from app.keymoment_utils import detect_key_moments

router = APIRouter(prefix="/api/videos", tags=["Key Moments"])


def run_keymoment_pipeline(video_id: str):
    db = SessionLocal()
    try:
        status_row = db.query(KeyMomentStatus).filter(KeyMomentStatus.video_id == video_id).first()
        if not status_row:
            status_row = KeyMomentStatus(video_id=video_id, status="PROCESSING")
            db.add(status_row)
        else:
            status_row.status = "PROCESSING"
        db.commit()

        transcript = db.query(Transcript).filter(Transcript.video_id == video_id).first()
        if not transcript:
            status_row.status = "FAILED"
            db.commit()
            return

        raw_segments = json.loads(transcript.segments_json)
        result = detect_key_moments(raw_segments)

        # purane topics/moments hatao (regenerate case)
        db.query(Topic).filter(Topic.video_id == video_id).delete()
        db.query(KeyMoment).filter(KeyMoment.video_id == video_id).delete()

        for t in result["topics"]:
            db.add(Topic(video_id=video_id, title=t["title"],
                          start_time=t["start_time"], end_time=t["end_time"]))

        for m in result["key_moments"]:
            db.add(KeyMoment(
                video_id=video_id,
                topic_title=None,
                start_time=m["start_time"],
                end_time=m["end_time"],
                text=m["text"],
                importance_score=str(m["importance_score"]),
            ))

        status_row.status = "COMPLETED"
        db.commit()
    except Exception:
        status_row = db.query(KeyMomentStatus).filter(KeyMomentStatus.video_id == video_id).first()
        if status_row:
            status_row.status = "FAILED"
            db.commit()
    finally:
        db.close()


@router.post("/{video_id}/keymoments/generate", status_code=status.HTTP_202_ACCEPTED)
def generate_keymoments(
    video_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or video.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Video not found.")

    existing = db.query(KeyMomentStatus).filter(KeyMomentStatus.video_id == video_id).first()
    if existing and existing.status == "PROCESSING":
        return {"message": "Already processing. Please wait."}

    background_tasks.add_task(run_keymoment_pipeline, video_id)
    return {"message": "Key moment detection started."}


@router.get("/{video_id}/keymoments")
def get_keymoments(
    video_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or video.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Video not found.")

    status_row = db.query(KeyMomentStatus).filter(KeyMomentStatus.video_id == video_id).first()
    current_status = status_row.status if status_row else "NOT_STARTED"

    topics = db.query(Topic).filter(Topic.video_id == video_id).order_by(Topic.start_time).all()
    moments = db.query(KeyMoment).filter(KeyMoment.video_id == video_id).order_by(KeyMoment.start_time).all()

    return {
        "status": current_status,
        "topics": [{"title": t.title, "start_time": t.start_time, "end_time": t.end_time} for t in topics],
        "key_moments": [
            {
                "start_time": m.start_time,
                "end_time": m.end_time,
                "text": m.text,
                "score": float(m.importance_score),
            }
            for m in moments
        ],
    } """
    
    
    
    
    
    
    
    
    
    
    
    

"""
routers/keymoments.py
----------------------
Module 3 ke API endpoints.
NOTE: Yeh Transcript table par depend karta hai (Module 2 se aana chahiye).
"""
 
import json
 
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
 
from app.database import get_db, SessionLocal
from app.dependencies import get_current_user
from app.models import User, Video, Transcript, Topic, KeyMoment, KeyMomentStatus
from app.keymoment_utils import detect_key_moments
 
router = APIRouter(prefix="/api/videos", tags=["Key Moments"])
 
 
def run_keymoment_pipeline(video_id: str):
    db = SessionLocal()
    try:
        status_row = db.query(KeyMomentStatus).filter(KeyMomentStatus.video_id == video_id).first()
        if not status_row:
            status_row = KeyMomentStatus(video_id=video_id, status="PROCESSING")
            db.add(status_row)
        else:
            status_row.status = "PROCESSING"
        db.commit()
 
        transcript = db.query(Transcript).filter(Transcript.video_id == video_id).first()
        if not transcript or transcript.status != "COMPLETED":
            # Transcript abhi ready nahi hai (ya kabhi generate hi nahi hua) —
            # isliye key moments generate karna galat/khaali result dega.
            status_row.status = "FAILED"
            db.commit()
            return
 
        raw_segments = json.loads(transcript.segments_json)
        result = detect_key_moments(raw_segments)
 
        # purane topics/moments hatao (regenerate case)
        db.query(Topic).filter(Topic.video_id == video_id).delete()
        db.query(KeyMoment).filter(KeyMoment.video_id == video_id).delete()
 
        for t in result["topics"]:
            db.add(Topic(video_id=video_id, title=t["title"],
                          start_time=t["start_time"], end_time=t["end_time"]))
 
        for m in result["key_moments"]:
            db.add(KeyMoment(
                video_id=video_id,
                topic_title=None,
                start_time=m["start_time"],
                end_time=m["end_time"],
                text=m["text"],
                importance_score=str(m["importance_score"]),
            ))
 
        status_row.status = "COMPLETED"
        db.commit()
    except Exception:
        status_row = db.query(KeyMomentStatus).filter(KeyMomentStatus.video_id == video_id).first()
        if status_row:
            status_row.status = "FAILED"
            db.commit()
    finally:
        db.close()
 
 
@router.post("/{video_id}/keymoments/generate", status_code=status.HTTP_202_ACCEPTED)
def generate_keymoments(
    video_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or video.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Video not found.")
 
    existing = db.query(KeyMomentStatus).filter(KeyMomentStatus.video_id == video_id).first()
    if existing and existing.status == "PROCESSING":
        return {"message": "Already processing. Please wait."}
 
    background_tasks.add_task(run_keymoment_pipeline, video_id)
    return {"message": "Key moment detection started."}
 
 
@router.get("/{video_id}/keymoments")
def get_keymoments(
    video_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or video.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Video not found.")
 
    status_row = db.query(KeyMomentStatus).filter(KeyMomentStatus.video_id == video_id).first()
    current_status = status_row.status if status_row else "NOT_STARTED"
 
    topics = db.query(Topic).filter(Topic.video_id == video_id).order_by(Topic.start_time).all()
    moments = db.query(KeyMoment).filter(KeyMoment.video_id == video_id).order_by(KeyMoment.start_time).all()
 
    return {
        "status": current_status,
        "topics": [{"title": t.title, "start_time": t.start_time, "end_time": t.end_time} for t in topics],
        "key_moments": [
            {
                "start_time": m.start_time,
                "end_time": m.end_time,
                "text": m.text,
                "score": float(m.importance_score),
            }
            for m in moments
        ],
    }







