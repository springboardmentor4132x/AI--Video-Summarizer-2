# Architecture

ClipMind AI: upload video → FFmpeg extract → Whisper transcript → embeddings and topic analysis → summaries / key moments.

```
Frontend (Next.js :3000)
        |
        v
Backend (FastAPI :8000)
        |-- PostgreSQL
        |-- Redis + Celery worker
        +-- /data/media files
```

## Video processing

1. `POST /videos/upload` saves the file (`backend/app/api/videos.py`)
2. `POST /videos/{id}/process` queues `ffmpeg_extract`
3. Celery task `backend/app/tasks/video.py` calls `backend/app/services/ffmpeg.py`
4. Job status is stored in `processing_jobs`
5. Transcription stores Whisper's timed segments in `transcripts.segments`

## Transcript analysis (Module 3)

After transcription completes, `key_moments` is queued automatically. `backend/app/services/analysis.py` combines timed Whisper segments into bounded chunks, embeds them with `all-MiniLM-L6-v2` from Sentence Transformers, and compares neighboring vectors with cosine similarity. If the optional embedding package/model is unavailable, a token-overlap fallback keeps local development and tests usable.

Similarity drops are treated as candidate topic boundaries, not proof of a topic change. Highlight scores currently combine content density (55%), marker keywords (30%), and an endpoint-position signal (15%). These weights are intentionally explicit starting points to tune against project data. Candidates are ranked by score and overlapping selections are suppressed before persistence.

Topics are stored in `topics`; key moments store their topic, timestamp range, transcript text, and score. `GET /videos/{id}/analysis` feeds the frontend, where topic and highlight timestamps seek the video player. Re-run analysis with `POST /videos/{id}/analysis` after a completed transcript.

## AI analytics

Reserved in `database/alembic/versions/001_initial.py`:

- `transcripts`
- `summaries`
- `key_moments`
- `analytics_events`
- `topics`

Job types already exist: `transcribe`, `summarize`, `key_moments`.

Apply `database/alembic/versions/003_topics_and_key_moment_context.py` with `alembic -c ..\database\alembic.ini upgrade head` before starting the worker.
