# Folder structure

```
AIVIDEOSUMMARIZER/
  backend/      FastAPI app, SQLAlchemy models, workers
  frontend/     Next.js UI
  database/     Alembic migrations + seeds
  docs/         Architecture and API notes
  tests/        Backend unit tests, frontend test stubs
```

| Folder | Owns |
|---|---|
| `backend/app` | API, auth, FFmpeg pipeline, models |
| `frontend/app` | Pages and dashboards |
| `database/alembic` | PostgreSQL schema versions |
| `database/seeds` | Default admin and later fixtures |
| `docs` | Human docs |
| `tests/backend` | pytest |
| `tests/frontend` | UI tests (later) |
