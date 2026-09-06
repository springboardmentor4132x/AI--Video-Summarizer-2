from celery import Celery

from app.config import settings

celery_app = Celery(
    "clipmind",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.video"],
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)
