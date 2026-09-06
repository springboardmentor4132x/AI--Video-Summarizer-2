import threading

from app.config import settings


def _redis_available() -> bool:
    try:
        import redis

        redis.Redis.from_url(settings.redis_url, socket_connect_timeout=0.5).ping()
        return True
    except Exception:
        return False


def enqueue_ffmpeg(job_id: str, video_id: str) -> None:
    from app.tasks.video import process_ffmpeg

    if _redis_available():
        process_ffmpeg.delay(job_id, video_id)
        return
    threading.Thread(target=process_ffmpeg, args=(job_id, video_id), daemon=True).start()


def enqueue_transcription(job_id: str, video_id: str) -> None:
    from app.tasks.video import process_transcription

    if _redis_available():
        process_transcription.delay(job_id, video_id)
        return
    threading.Thread(target=process_transcription, args=(job_id, video_id), daemon=True).start()


def enqueue_summary(job_id: str, video_id: str) -> None:
    from app.tasks.video import process_summary

    if _redis_available():
        process_summary.delay(job_id, video_id)
        return
    threading.Thread(target=process_summary, args=(job_id, video_id), daemon=True).start()


def enqueue_analysis(job_id: str, video_id: str) -> None:
    from app.tasks.video import process_analysis

    if _redis_available():
        process_analysis.delay(job_id, video_id)
        return
    threading.Thread(target=process_analysis, args=(job_id, video_id), daemon=True).start()
