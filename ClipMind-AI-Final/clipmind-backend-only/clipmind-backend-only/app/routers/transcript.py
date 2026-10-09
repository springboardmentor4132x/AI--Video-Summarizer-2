"""
routers/transcript.py
----------------------
Module 2 ke API endpoints: video ki audio se real transcript generate karna
(local Whisper model se), transcript se summary generate karna, aur
transcript ko doosri languages mein translate karna.
"""
 
import json
import traceback
 
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
 
from app.database import get_db, SessionLocal
from app.dependencies import get_current_user
from app.models import User, Video, Transcript
from app.transcript_utils import extract_audio, transcribe_audio, generate_summary
from app.translate_utils import translate_text, SUPPORTED_LANGUAGES
 
router = APIRouter(prefix="/api/videos", tags=["Transcript"])
 
 
def run_transcript_pipeline(video_id: str, video_path: str):
    db = SessionLocal()
    try:
        transcript = db.query(Transcript).filter(Transcript.video_id == video_id).first()
        if not transcript:
            transcript = Transcript(video_id=video_id, segments_json="[]", status="PROCESSING")
            db.add(transcript)
        else:
            transcript.status = "PROCESSING"
        db.commit()
 
        audio_path = video_path + ".wav"
        ok, ffmpeg_error = extract_audio(video_path, audio_path)
        if not ok:
            print(f"[transcript] ffmpeg audio extraction FAILED for video {video_id}:")
            print(ffmpeg_error)
            transcript.status = "FAILED"
            db.commit()
            return
 
        result = transcribe_audio(audio_path)
 
        transcript.full_text = result["full_text"]
        transcript.segments_json = json.dumps(result["segments"])
        transcript.status = "COMPLETED"
        db.commit()
    except Exception:
        print(f"[transcript] Pipeline CRASHED for video {video_id}:")
        traceback.print_exc()
        transcript = db.query(Transcript).filter(Transcript.video_id == video_id).first()
        if transcript:
            transcript.status = "FAILED"
            db.commit()
    finally:
        db.close()
 
 
@router.post("/{video_id}/transcript/generate", status_code=status.HTTP_202_ACCEPTED)
def generate_transcript(
    video_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or video.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Video not found.")
 
    existing = db.query(Transcript).filter(Transcript.video_id == video_id).first()
    if existing and existing.status == "PROCESSING":
        return {"message": "Already processing. Please wait."}
 
    background_tasks.add_task(run_transcript_pipeline, video_id, video.file_path)
    return {"message": "Transcript generation started."}
 
 
@router.get("/{video_id}/transcript")
def get_transcript(
    video_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or video.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Video not found.")
 
    transcript = db.query(Transcript).filter(Transcript.video_id == video_id).first()
    if not transcript:
        return {"status": "NOT_STARTED", "full_text": None, "segments": []}
 
    return {
        "status": transcript.status,
        "full_text": transcript.full_text,
        "segments": json.loads(transcript.segments_json) if transcript.segments_json else [],
    }
 
 
@router.get("/{video_id}/transcript/languages")
def get_supported_languages(current_user: User = Depends(get_current_user)):
    """Frontend ke language-picker panel ke liye supported languages ki list."""
    return {"languages": [{"code": code, "name": name} for code, name in SUPPORTED_LANGUAGES.items()]}
 
 
@router.get("/{video_id}/transcript/translate")
def translate_transcript(
    video_id: str,
    lang: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Transcript ka full_text diye gaye language mein translate karke deta hai."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or video.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Video not found.")
 
    transcript = db.query(Transcript).filter(Transcript.video_id == video_id).first()
    if not transcript or transcript.status != "COMPLETED":
        raise HTTPException(status_code=400, detail="Transcript abhi ready nahi hai.")
 
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail="Yeh language abhi supported nahi hai.")
 
    try:
        translated = translate_text(transcript.full_text or "", lang)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Translation failed: {type(e).__name__}: {e}",
        )
 
    return {"language": lang, "language_name": SUPPORTED_LANGUAGES[lang], "translated_text": translated}
 
 
@router.get("/{video_id}/summary")
def get_summary(
    video_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or video.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Video not found.")
 
    transcript = db.query(Transcript).filter(Transcript.video_id == video_id).first()
    if not transcript or transcript.status != "COMPLETED":
        return {
            "status": transcript.status if transcript else "NOT_STARTED",
            "short_summary": None,
            "topics": [],
        }
 
    segments = json.loads(transcript.segments_json) if transcript.segments_json else []
    summary = generate_summary(transcript.full_text or "", segments)
    return {"status": "COMPLETED", **summary}
 







