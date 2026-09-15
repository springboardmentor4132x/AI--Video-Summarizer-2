"""
routers/transcript.py
Module 2 - Transcript Generation aur AI Summarization APIs.
"""

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Video, VideoStatus, Transcript, TranscriptStatus, Summary, SummaryStatus
from app.schemas import (
    TranscriptOut, TranscriptActionResponse,
    SummaryOut, SummaryActionResponse,
)
from app.config import UPLOAD_DIR
from app.whisper_utils import generate_transcript
from app.summarization_utils import generate_summaries

router = APIRouter(prefix="/api/videos", tags=["Transcript & Summary"])


def _get_owned_video(video_id: str, current_user: User, db: Session) -> Video:
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found.")
    if video.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have access to this video.")
    return video


def run_transcript_pipeline(transcript_id: str, video_path: str):
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        transcript = db.query(Transcript).filter(Transcript.id == transcript_id).first()
        if not transcript:
            return

        audio_path = str(Path(UPLOAD_DIR) / "audio" / f"{transcript_id}.wav")
        result = generate_transcript(video_path, audio_path)

        if result["success"]:
            transcript.transcript_text = result["transcript_text"]
            transcript.status = TranscriptStatus.COMPLETED
            transcript.error_message = None
        else:
            transcript.status = TranscriptStatus.FAILED
            transcript.error_message = result["error"]

        db.commit()
    finally:
        db.close()


def run_summary_pipeline(summary_id: str, transcript_text: str):
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        summary = db.query(Summary).filter(Summary.id == summary_id).first()
        if not summary:
            return

        result = generate_summaries(transcript_text)

        if result["success"]:
            summary.short_summary = result["short_summary"]
            summary.detailed_summary = result["detailed_summary"]
            summary.status = SummaryStatus.COMPLETED
            summary.error_message = None
        else:
            summary.status = SummaryStatus.FAILED
            summary.error_message = result["error"]

        db.commit()
    finally:
        db.close()


@router.post("/{video_id}/transcript/generate", response_model=TranscriptActionResponse)
def generate_video_transcript(
    video_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    video = _get_owned_video(video_id, current_user, db)

    if video.status != VideoStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Video is not ready yet (current status: {video.status.value}). "
                   f"Wait for upload processing to complete first.",
        )

    transcript = db.query(Transcript).filter(Transcript.video_id == video_id).first()

    if transcript and transcript.status == TranscriptStatus.PROCESSING:
        return TranscriptActionResponse(
            message="Transcript generation is already in progress.",
            transcript=transcript,
        )

    if transcript is None:
        transcript = Transcript(
            video_id=video_id,
            user_id=current_user.id,
            status=TranscriptStatus.PROCESSING,
        )
        db.add(transcript)
    else:
        transcript.status = TranscriptStatus.PROCESSING
        transcript.error_message = None

    db.commit()
    db.refresh(transcript)

    background_tasks.add_task(run_transcript_pipeline, transcript.id, video.file_path)

    return TranscriptActionResponse(
        message="Transcript generation started.",
        transcript=transcript,
    )


@router.get("/{video_id}/transcript", response_model=TranscriptOut)
def get_video_transcript(
    video_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_owned_video(video_id, current_user, db)

    transcript = db.query(Transcript).filter(Transcript.video_id == video_id).first()
    if not transcript:
        raise HTTPException(
            status_code=404,
            detail="No transcript found for this video yet. Call the /transcript/generate endpoint first.",
        )
    return transcript


@router.post("/{video_id}/summary/generate", response_model=SummaryActionResponse)
def generate_video_summary(
    video_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_owned_video(video_id, current_user, db)

    transcript = db.query(Transcript).filter(Transcript.video_id == video_id).first()
    if not transcript or transcript.status != TranscriptStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail="Transcript must be generated (status = completed) before summarization can start.",
        )

    summary = db.query(Summary).filter(Summary.transcript_id == transcript.id).first()

    if summary and summary.status == SummaryStatus.PROCESSING:
        return SummaryActionResponse(
            message="Summary generation is already in progress.",
            summary=summary,
        )

    if summary is None:
        summary = Summary(
            transcript_id=transcript.id,
            video_id=video_id,
            user_id=current_user.id,
            status=SummaryStatus.PROCESSING,
        )
        db.add(summary)
    else:
        summary.status = SummaryStatus.PROCESSING
        summary.error_message = None

    db.commit()
    db.refresh(summary)

    background_tasks.add_task(run_summary_pipeline, summary.id, transcript.transcript_text)

    return SummaryActionResponse(
        message="Summary generation started.",
        summary=summary,
    )


@router.get("/{video_id}/summary", response_model=SummaryOut)
def get_video_summary(
    video_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_owned_video(video_id, current_user, db)

    transcript = db.query(Transcript).filter(Transcript.video_id == video_id).first()
    if not transcript:
        raise HTTPException(status_code=404, detail="No transcript found for this video yet.")

    summary = db.query(Summary).filter(Summary.transcript_id == transcript.id).first()
    if not summary:
        raise HTTPException(
            status_code=404,
            detail="No summary found for this video yet. Call the /summary/generate endpoint first.",
        )
    return summary