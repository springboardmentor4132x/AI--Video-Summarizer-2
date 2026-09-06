# ClipMind AI

AI video summarization and key moments platform.

## Layout

```
backend/     FastAPI + Celery
frontend/    Next.js
database/    PostgreSQL migrations + seeds
docs/        Architecture and API
tests/       pytest (backend) + frontend stubs
```

## Stack

- Frontend: Next.js + Tailwind
- Backend: FastAPI
- Database: PostgreSQL
- Queue: Redis + Celery
- Video: FFmpeg

## Start with Docker

```bash
docker compose up --build
```

- App: http://localhost:3000
- API docs: http://localhost:8000/docs

Default admin: `admin@clipmind.ai` / `Admin123!`

## Local dev

### With Docker dependencies

1. `docker compose up postgres redis`
2. Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic -c ..\database\alembic.ini upgrade head
uvicorn app.main:app --reload
```

Worker:

```bash
cd backend
.venv\Scripts\activate
celery -A app.worker.celery_app worker --loglevel=info --pool=solo
```

3. Frontend: `cd frontend && npm install && npm run dev`

### Without Docker

The repository includes a PostgreSQL data directory for local development. From the repository root, start it on port `55432` using the PostgreSQL installation on your machine:

```powershell
& "C:\Program Files\PostgreSQL\17\bin\pg_ctl.exe" -D "$PWD\database\pgdata" -o '"-p" "55432"' -l "$PWD\database\pgdata\server.log" start
```

Then run the backend:

```powershell
$env:DATABASE_URL="postgresql://clipmind@localhost:55432/clipmind"
cd backend
..\.venv\Scripts\python.exe -m alembic -c ..\database\alembic.ini upgrade head
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

In another terminal:

```powershell
cd frontend
npx next dev --hostname 127.0.0.1 --port 3000
```

Redis is optional for local development. When Redis is unavailable, the queue service runs processing tasks in background threads.

## Tests

```bash
cd backend
.venv\Scripts\activate
pip install -r requirements.txt
cd ..
pytest
```

## Implemented features

- JWT auth and four roles
- Video upload and history
- FFmpeg: duration, thumbnail, 16 kHz audio
- Whisper transcript generation with timestamped segments
- Transcript chunking and topic segmentation
- Sentence Transformer embeddings with a local lexical fallback
- Importance scoring and overlapping highlight suppression
- Persisted topics and key moments with timestamps and transcript text
- Clickable topic and highlight timestamps in the video player
- API endpoints for analysis retrieval and reruns

Apply database migrations before starting the backend. See `docs/architecture.md` for the Module 3 processing flow and scoring rationale.
