"""
main.py
--------
FastAPI application entrypoint.

Run with:
    uvicorn app.main:app --reload

Other teammates will later add their own routers here too, e.g.:
    from app.routes import video_routes
    app.include_router(video_routes.router)
"""

import os
# Fix OpenBLAS thread allocation failure in multi-threaded Python/FastAPI environment
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["OPENBLAS_MAIN_FREE"] = "1"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base, SessionLocal
from app.routes import auth_routes, video_routes
from app.models import Video

# Create database tables automatically if they do not exist
Base.metadata.create_all(bind=engine)

# Reset videos stuck in 'processing' state due to past backend restarts/crashes
db_startup = SessionLocal()
try:
    stuck_videos = db_startup.query(Video).filter(Video.status == "processing").all()
    if stuck_videos:
        print(f"[Startup] Found {len(stuck_videos)} video(s) stuck in processing status. Resetting to 'uploaded'.")
        for v in stuck_videos:
            v.status = "uploaded"
        db_startup.commit()
finally:
    db_startup.close()

app = FastAPI(
    title="ClipMind AI - Backend",
    description="Backend API for ClipMind AI (Infosys Springboard project)",
    version="0.1.0",
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(video_routes.router)

from app.auth import get_current_user
from app.models import User
from app.schemas import UserOut
from fastapi import Depends

@app.get("/users/me", response_model=UserOut, tags=["Users"])
def read_users_me_alias(current_user: User = Depends(get_current_user)):
    """Frontend compatibility alias bridging Utkarsh's API to Khushi's Auth layer."""
    return current_user

from sqlalchemy.orm import Session
from app.database import get_db

@app.get("/users", response_model=list[UserOut], tags=["Users"])
def get_all_users_alias(db: Session = Depends(get_db)):
    """Endpoint expected by Utkarsh's Dashboard."""
    return db.query(User).all()


from app.routes.video_routes import get_analytics_dashboard
app.get("/analytics/dashboard", tags=["Analytics"])(get_analytics_dashboard)

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "ClipMind AI backend is running"}