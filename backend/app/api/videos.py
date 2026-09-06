import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.db import get_db
from app.deps import get_current_user, get_current_user_optional_query
from app.models.engagement import AnalyticsEvent, AuditLog
from app.models.user import User, UserRole
from app.models.video import ContentStatus, JobStatus, JobType, KeyMoment, ProcessingJob, Summary, Topic, Transcript, Video, VideoStatus
from app.schemas.video import AnalysisOut, JobOut, KeyMomentOut, SummaryOut, TopicOut, TranscriptOut, TranscriptUpdate, VideoOut, VideoUpdate
from app.services.queue import enqueue_analysis, enqueue_ffmpeg, enqueue_summary
from app.services.storage import ALLOWED_CONTENT_TYPES, ALLOWED_EXTENSIONS, resolve_storage_path, video_dir

router = APIRouter(prefix="/videos", tags=["videos"])

UPLOAD_ROLES = {UserRole.CONTENT_CREATOR, UserRole.EDUCATOR, UserRole.ADMINISTRATOR}


def to_video_out(video: Video) -> VideoOut:
    owner_name = video.owner.full_name if video.owner else None
    return VideoOut(
        id=str(video.id),
        owner_id=str(video.owner_id),
        owner_name=owner_name,
        original_filename=video.original_filename,
        title=video.title,
        description=video.description,
        status=video.status,
        is_public=video.is_public,
        duration=video.duration,
        width=video.width,
        height=video.height,
        file_size=video.file_size,
        error_message=video.error_message,
        has_thumbnail=bool(video.thumbnail_path),
        has_audio=bool(video.audio_path),
        created_at=video.created_at,
    )


def to_job_out(job: ProcessingJob) -> JobOut:
    return JobOut(
        id=str(job.id),
        video_id=str(job.video_id),
        job_type=job.job_type,
        status=job.status,
        progress=job.progress,
        error=job.error,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


def to_transcript_out(transcript: Transcript) -> TranscriptOut:
    return TranscriptOut(id=str(transcript.id), video_id=str(transcript.video_id), status=transcript.status,
                         language=transcript.language, full_text=transcript.full_text,
                         edited_text=transcript.edited_text, error_message=transcript.error_message,
                         created_at=transcript.created_at, updated_at=transcript.updated_at)


def to_summary_out(summary: Summary) -> SummaryOut:
    return SummaryOut(id=str(summary.id), video_id=str(summary.video_id), status=summary.status,
                      short_text=summary.short_text, detailed_text=summary.detailed_text,
                      keywords=summary.keywords or [], error_message=summary.error_message,
                      created_at=summary.created_at, updated_at=summary.updated_at)


def to_topic_out(topic: Topic) -> TopicOut:
        return TopicOut(id=str(topic.id), video_id=str(topic.video_id), start_sec=topic.start_sec,
                                        end_sec=topic.end_sec, title=topic.title, transcript_text=topic.transcript_text,
                                        created_at=topic.created_at)


def to_key_moment_out(moment: KeyMoment) -> KeyMomentOut:
        return KeyMomentOut(id=str(moment.id), video_id=str(moment.video_id), topic_id=str(moment.topic_id) if moment.topic_id else None,
                                                start_sec=moment.start_sec, end_sec=moment.end_sec, title=moment.title,
                                                transcript_text=moment.transcript_text, score=moment.score,
                                                moment_type=moment.moment_type, created_at=moment.created_at)


def can_view(user: User, video: Video) -> bool:
    if user.role == UserRole.ADMINISTRATOR:
        return True
    if video.owner_id == user.id:
        return True
    if video.is_public and video.status == VideoStatus.READY:
        return True
    if user.role == UserRole.LEARNER and video.is_public:
        return True
    return False


def can_manage(user: User, video: Video) -> bool:
    return user.role == UserRole.ADMINISTRATOR or video.owner_id == user.id


@router.post("/upload", response_model=VideoOut, status_code=status.HTTP_201_CREATED)
async def upload_video(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    description: str | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VideoOut:
    if current_user.role not in UPLOAD_ROLES:
        raise HTTPException(status_code=403, detail="Your role cannot upload videos")

    filename = file.filename or "video.mp4"
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported format. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}")
    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Invalid video content type")

    video_id = uuid.uuid4()
    folder = video_dir(str(current_user.id), str(video_id))
    dest = folder / f"original{suffix}"
    max_bytes = settings.max_upload_mb * 1024 * 1024
    size = 0
    with dest.open("wb") as handle:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > max_bytes:
                handle.close()
                dest.unlink(missing_ok=True)
                raise HTTPException(status_code=400, detail=f"File exceeds {settings.max_upload_mb} MB limit")
            handle.write(chunk)

    video = Video(
        id=video_id,
        owner_id=current_user.id,
        original_filename=filename,
        storage_path=str(dest),
        content_type=file.content_type,
        file_size=size,
        title=(title or Path(filename).stem).strip(),
        description=description,
        status=VideoStatus.UPLOADED,
        is_public=True,
    )
    db.add(video)
    db.flush()
    db.add(AuditLog(actor_id=current_user.id, action="video.upload", detail={"video_id": str(video.id)}))
    db.add(
        AnalyticsEvent(
            user_id=current_user.id,
            video_id=video.id,
            event_type="upload",
            payload={"bytes": size},
        )
    )
    db.commit()
    db.refresh(video)
    video.owner = current_user
    return to_video_out(video)


@router.get("", response_model=list[VideoOut])
def list_videos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[VideoOut]:
    query = select(Video).options(joinedload(Video.owner)).order_by(Video.created_at.desc())
    if current_user.role == UserRole.ADMINISTRATOR:
        videos = db.scalars(query).unique().all()
    elif current_user.role == UserRole.LEARNER:
        videos = db.scalars(query.where(or_(Video.is_public.is_(True), Video.owner_id == current_user.id))).unique().all()
    else:
        videos = db.scalars(query.where(or_(Video.owner_id == current_user.id, Video.is_public.is_(True)))).unique().all()
    return [to_video_out(v) for v in videos]


@router.get("/{video_id}", response_model=VideoOut)
def get_video(
    video_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VideoOut:
    video = db.scalar(select(Video).options(joinedload(Video.owner)).where(Video.id == video_id))
    if video is None or not can_view(current_user, video):
        raise HTTPException(status_code=404, detail="Video not found")
    db.add(
        AnalyticsEvent(
            user_id=current_user.id,
            video_id=video.id,
            event_type="view",
            payload={},
        )
    )
    db.commit()
    return to_video_out(video)


@router.patch("/{video_id}", response_model=VideoOut)
def update_video(
    video_id: uuid.UUID,
    payload: VideoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VideoOut:
    video = db.scalar(select(Video).options(joinedload(Video.owner)).where(Video.id == video_id))
    if video is None or not can_manage(current_user, video):
        raise HTTPException(status_code=404, detail="Video not found")
    if payload.title is not None:
        video.title = payload.title.strip()
    if payload.description is not None:
        video.description = payload.description
    if payload.is_public is not None:
        video.is_public = payload.is_public
    db.add(video)
    db.commit()
    db.refresh(video)
    return to_video_out(video)


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_video(
    video_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    video = db.get(Video, video_id)
    if video is None or not can_manage(current_user, video):
        raise HTTPException(status_code=404, detail="Video not found")
    db.delete(video)
    db.commit()


@router.post("/{video_id}/process", response_model=JobOut)
def process_video(
    video_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobOut:
    video = db.get(Video, video_id)
    if video is None or not can_manage(current_user, video):
        raise HTTPException(status_code=404, detail="Video not found")
    job = ProcessingJob(video_id=video.id, job_type=JobType.FFMPEG_EXTRACT, status=JobStatus.QUEUED, progress=0)
    video.status = VideoStatus.PROCESSING
    db.add(job)
    db.add(video)
    db.commit()
    db.refresh(job)
    enqueue_ffmpeg(str(job.id), str(video.id))
    return to_job_out(job)


@router.get("/{video_id}/jobs", response_model=list[JobOut])
def list_jobs(
    video_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[JobOut]:
    video = db.get(Video, video_id)
    if video is None or not can_view(current_user, video):
        raise HTTPException(status_code=404, detail="Video not found")
    jobs = db.scalars(
        select(ProcessingJob).where(ProcessingJob.video_id == video_id).order_by(ProcessingJob.created_at.desc())
    ).all()
    return [to_job_out(j) for j in jobs]


@router.get("/{video_id}/transcript", response_model=TranscriptOut)
def get_transcript(video_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> TranscriptOut:
    video = db.get(Video, video_id)
    if video is None or not can_view(current_user, video):
        raise HTTPException(status_code=404, detail="Video not found")
    transcript = db.scalar(select(Transcript).where(Transcript.video_id == video_id))
    if transcript is None:
        transcript = Transcript(video_id=video_id)
        db.add(transcript)
        db.commit()
        db.refresh(transcript)
    return to_transcript_out(transcript)


@router.patch("/{video_id}/transcript", response_model=TranscriptOut)
def update_transcript(video_id: uuid.UUID, payload: TranscriptUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> TranscriptOut:
    video = db.get(Video, video_id)
    if video is None or not can_manage(current_user, video):
        raise HTTPException(status_code=404, detail="Video not found")
    transcript = db.scalar(select(Transcript).where(Transcript.video_id == video_id))
    if transcript is None:
        raise HTTPException(status_code=404, detail="Transcript not found")
    transcript.edited_text = payload.text.strip()
    db.commit()
    db.refresh(transcript)
    return to_transcript_out(transcript)


@router.get("/{video_id}/summary", response_model=SummaryOut)
def get_summary(video_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> SummaryOut:
    video = db.get(Video, video_id)
    if video is None or not can_view(current_user, video):
        raise HTTPException(status_code=404, detail="Video not found")
    summary = db.scalar(select(Summary).where(Summary.video_id == video_id))
    if summary is None:
        summary = Summary(video_id=video_id)
        db.add(summary)
        db.commit()
        db.refresh(summary)
    return to_summary_out(summary)


@router.post("/{video_id}/summary", response_model=JobOut, status_code=status.HTTP_202_ACCEPTED)
def generate_summary(video_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> JobOut:
    video = db.get(Video, video_id)
    if video is None or not can_manage(current_user, video):
        raise HTTPException(status_code=404, detail="Video not found")
    transcript = db.scalar(select(Transcript).where(Transcript.video_id == video_id))
    if transcript is None or transcript.status != ContentStatus.COMPLETED:
        raise HTTPException(status_code=409, detail="A completed transcript is required")
    summary = db.scalar(select(Summary).where(Summary.video_id == video_id))
    active = db.scalar(select(ProcessingJob).where(ProcessingJob.video_id == video_id, ProcessingJob.job_type == JobType.SUMMARIZE, ProcessingJob.status.in_([JobStatus.QUEUED, JobStatus.RUNNING])))
    if active:
        return to_job_out(active)
    if summary is None:
        summary = Summary(video_id=video_id)
        db.add(summary)
        db.flush()
    summary.status = ContentStatus.PROCESSING
    summary.error_message = None
    job = ProcessingJob(video_id=video_id, job_type=JobType.SUMMARIZE, status=JobStatus.QUEUED)
    db.add(job)
    db.commit()
    db.refresh(job)
    enqueue_summary(str(job.id), str(video_id))
    return to_job_out(job)


@router.get("/{video_id}/analysis", response_model=AnalysisOut)
def get_analysis(video_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> AnalysisOut:
    video = db.get(Video, video_id)
    if video is None or not can_view(current_user, video):
        raise HTTPException(status_code=404, detail="Video not found")
    topics = db.scalars(select(Topic).where(Topic.video_id == video_id).order_by(Topic.start_sec)).all()
    moments = db.scalars(select(KeyMoment).where(KeyMoment.video_id == video_id).order_by(KeyMoment.start_sec)).all()
    return AnalysisOut(topics=[to_topic_out(topic) for topic in topics], key_moments=[to_key_moment_out(moment) for moment in moments])


@router.post("/{video_id}/analysis", response_model=JobOut, status_code=status.HTTP_202_ACCEPTED)
def rerun_analysis(video_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> JobOut:
    video = db.get(Video, video_id)
    if video is None or not can_manage(current_user, video):
        raise HTTPException(status_code=404, detail="Video not found")
    transcript = db.scalar(select(Transcript).where(Transcript.video_id == video_id))
    if transcript is None or transcript.status != ContentStatus.COMPLETED:
        raise HTTPException(status_code=409, detail="A completed transcript is required")
    active = db.scalar(select(ProcessingJob).where(ProcessingJob.video_id == video_id, ProcessingJob.job_type == JobType.KEY_MOMENTS, ProcessingJob.status.in_([JobStatus.QUEUED, JobStatus.RUNNING])))
    if active:
        return to_job_out(active)
    job = ProcessingJob(video_id=video_id, job_type=JobType.KEY_MOMENTS, status=JobStatus.QUEUED)
    db.add(job)
    db.commit()
    db.refresh(job)
    enqueue_analysis(str(job.id), str(video_id))
    return to_job_out(job)


@router.get("/{video_id}/stream")
def stream_video(
    video_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional_query),
):
    video = db.get(Video, video_id)
    if video is None or not can_view(current_user, video):
        raise HTTPException(status_code=404, detail="Video not found")
    path = resolve_storage_path(video.storage_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File missing on disk")
    return FileResponse(path, media_type=video.content_type or "video/mp4", filename=video.original_filename)


@router.get("/{video_id}/thumbnail")
def get_thumbnail(
    video_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional_query),
):
    video = db.get(Video, video_id)
    if video is None or not can_view(current_user, video) or not video.thumbnail_path:
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    path = resolve_storage_path(video.thumbnail_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Thumbnail missing on disk")
    return FileResponse(path, media_type="image/jpeg")
