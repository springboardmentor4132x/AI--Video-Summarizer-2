import uuid
from pathlib import Path

from app.db import SessionLocal
from app.models.video import ContentStatus, JobStatus, JobType, KeyMoment, ProcessingJob, Summary, Topic, Transcript, Video, VideoStatus
from app.services.analysis import analyze_transcript
from app.services.ffmpeg import FFmpegError, extract_audio, extract_thumbnail, probe_video
from app.services.ai import summarize_text, transcribe_audio
from app.services.queue import enqueue_analysis, enqueue_transcription
from app.worker import celery_app


def _update_job(db, job: ProcessingJob, *, status: JobStatus, progress: int, error: str | None = None) -> None:
    job.status = status
    job.progress = progress
    job.error = error
    db.add(job)
    db.commit()


@celery_app.task(name="app.tasks.video.process_ffmpeg")
def process_ffmpeg(job_id: str, video_id: str) -> None:
    db = SessionLocal()
    job = None
    video = None
    try:
        job = db.get(ProcessingJob, uuid.UUID(str(job_id)))
        video = db.get(Video, uuid.UUID(str(video_id)))
        if job is None or video is None:
            return

        video.status = VideoStatus.PROCESSING
        db.add(video)
        _update_job(db, job, status=JobStatus.RUNNING, progress=10)

        source = Path(video.storage_path)
        folder = source.parent
        audio_path = folder / "audio.wav"
        thumb_path = folder / "thumbnail.jpg"

        meta = probe_video(source)
        video.duration = meta["duration"] or None
        video.width = meta["width"]
        video.height = meta["height"]
        db.add(video)
        _update_job(db, job, status=JobStatus.RUNNING, progress=40)

        extract_audio(source, audio_path)
        video.audio_path = str(audio_path)
        db.add(video)
        _update_job(db, job, status=JobStatus.RUNNING, progress=75)

        at = 3.0 if (video.duration or 0) > 4 else 0.0
        extract_thumbnail(source, thumb_path, at_seconds=at)
        video.thumbnail_path = str(thumb_path)
        video.status = VideoStatus.READY
        video.error_message = None
        db.add(video)
        _update_job(db, job, status=JobStatus.COMPLETED, progress=100)
        transcript = db.query(Transcript).filter(Transcript.video_id == video.id).one_or_none()
        if transcript is None:
            transcript = Transcript(video_id=video.id, status=ContentStatus.PROCESSING)
            db.add(transcript)
        else:
            transcript.status = ContentStatus.PROCESSING
            transcript.error_message = None
        transcript_job = ProcessingJob(video_id=video.id, job_type=JobType.TRANSCRIBE, status=JobStatus.QUEUED)
        db.add(transcript_job)
        db.commit()
        enqueue_transcription(str(transcript_job.id), str(video.id))
    except FFmpegError as exc:
        if job:
            _update_job(db, job, status=JobStatus.FAILED, progress=job.progress, error=str(exc))
        if video:
            video.status = VideoStatus.FAILED
            video.error_message = str(exc)
            db.add(video)
            db.commit()
    except Exception as exc:  # noqa: BLE001
        if job:
            _update_job(db, job, status=JobStatus.FAILED, progress=job.progress, error=str(exc))
        if video:
            video.status = VideoStatus.FAILED
            video.error_message = str(exc)
            db.add(video)
            db.commit()
    finally:
        db.close()


@celery_app.task(name="app.tasks.video.process_transcription")
def process_transcription(job_id: str, video_id: str) -> None:
    db = SessionLocal()
    job = db.get(ProcessingJob, uuid.UUID(str(job_id)))
    video = db.get(Video, uuid.UUID(str(video_id)))
    transcript = db.query(Transcript).filter(Transcript.video_id == uuid.UUID(str(video_id))).one_or_none()
    try:
        if job is None or video is None or transcript is None or not video.audio_path:
            return
        _update_job(db, job, status=JobStatus.RUNNING, progress=10)
        transcript.status = ContentStatus.PROCESSING
        result = transcribe_audio(Path(video.audio_path))
        transcript.language = result["language"]
        transcript.full_text = result["full_text"]
        transcript.segments = result["segments"]
        transcript.status = ContentStatus.COMPLETED
        transcript.error_message = None
        db.add(transcript)
        _update_job(db, job, status=JobStatus.COMPLETED, progress=100)
        analysis_job = ProcessingJob(video_id=video.id, job_type=JobType.KEY_MOMENTS, status=JobStatus.QUEUED)
        db.add(analysis_job)
        db.commit()
        enqueue_analysis(str(analysis_job.id), str(video.id))
    except Exception as exc:  # noqa: BLE001
        if job:
            _update_job(db, job, status=JobStatus.FAILED, progress=job.progress, error=str(exc))
        if transcript:
            transcript.status = ContentStatus.FAILED
            transcript.error_message = str(exc)
            db.add(transcript)
            db.commit()
    finally:
        db.close()


@celery_app.task(name="app.tasks.video.process_summary")
def process_summary(job_id: str, video_id: str) -> None:
    db = SessionLocal()
    job = db.get(ProcessingJob, uuid.UUID(str(job_id)))
    summary = db.query(Summary).filter(Summary.video_id == uuid.UUID(str(video_id))).one_or_none()
    transcript = db.query(Transcript).filter(Transcript.video_id == uuid.UUID(str(video_id))).one_or_none()
    try:
        if job is None or summary is None or transcript is None:
            return
        _update_job(db, job, status=JobStatus.RUNNING, progress=10)
        short, detailed = summarize_text(transcript.edited_text or transcript.full_text or "")
        summary.short_text = short
        summary.detailed_text = detailed
        summary.status = ContentStatus.COMPLETED
        summary.error_message = None
        db.add(summary)
        _update_job(db, job, status=JobStatus.COMPLETED, progress=100)
    except Exception as exc:  # noqa: BLE001
        if job:
            _update_job(db, job, status=JobStatus.FAILED, progress=job.progress, error=str(exc))
        if summary:
            summary.status = ContentStatus.FAILED
            summary.error_message = str(exc)
            db.add(summary)
            db.commit()
    finally:
        db.close()


@celery_app.task(name="app.tasks.video.process_analysis")
def process_analysis(job_id: str, video_id: str) -> None:
    db = SessionLocal()
    job = db.get(ProcessingJob, uuid.UUID(str(job_id)))
    transcript = db.query(Transcript).filter(Transcript.video_id == uuid.UUID(str(video_id))).one_or_none()
    try:
        if job is None or transcript is None or transcript.status != ContentStatus.COMPLETED:
            return
        _update_job(db, job, status=JobStatus.RUNNING, progress=10)
        result = analyze_transcript(transcript.segments or [])
        db.query(KeyMoment).filter(KeyMoment.video_id == uuid.UUID(str(video_id))).delete()
        db.query(Topic).filter(Topic.video_id == uuid.UUID(str(video_id))).delete()
        topics: dict[int, Topic] = {}
        for item in result["topics"]:
            topic = Topic(video_id=uuid.UUID(str(video_id)), start_sec=item["start"], end_sec=item["end"], title=item["title"], transcript_text=item["text"])
            db.add(topic)
            db.flush()
            topics[item["index"]] = topic
        for item in result["highlights"]:
            db.add(KeyMoment(
                video_id=uuid.UUID(str(video_id)), topic_id=topics[item["topic_index"]].id,
                start_sec=item["start"], end_sec=item["end"], title=item["text"][:512],
                transcript_text=item["text"], score=item["score"], moment_type="highlight",
            ))
        _update_job(db, job, status=JobStatus.COMPLETED, progress=100)
    except Exception as exc:  # noqa: BLE001
        if job:
            _update_job(db, job, status=JobStatus.FAILED, progress=job.progress, error=str(exc))
    finally:
        db.close()
