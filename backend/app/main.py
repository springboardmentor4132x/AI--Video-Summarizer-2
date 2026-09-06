import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.jobs import router as jobs_router
from app.api.users import router as users_router
from app.api.videos import router as videos_router
from app.config import settings
from app.db import SessionLocal

for candidate in (Path(__file__).resolve().parents[2] / "database", Path("/database")):
    if candidate.exists():
        sys.path.insert(0, str(candidate))
        break

from seeds.seed_admin import seed_admin  # noqa: E402

app = FastAPI(
    title="ClipMind AI",
    description="Video summarization and key moments detection platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(videos_router)
app.include_router(jobs_router)


@app.on_event("startup")
def on_startup() -> None:
    db = SessionLocal()
    try:
        seed_admin(db)
    finally:
        db.close()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "clipmind-api"}
