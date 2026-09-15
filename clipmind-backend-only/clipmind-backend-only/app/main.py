"""
main.py
-------
FastAPI application ka entry point.

Run karne ke liye (backend/ folder ke andar se):
    uvicorn app.main:app --reload

Docs yahan milenge: http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.config import UPLOAD_DIR
from app.routers import auth, video, dashboard, transcript

# Database tables create karo (agar pehle se nahi hain)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ClipMind AI - Module 1 API",
    description="Project Initialization, Design Process and Core Setup",
    version="1.0.0",
)

# CORS - taaki React frontend (alag port par chal raha) backend ko call kar sake
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Uploaded videos/thumbnails ko serve karne ke liye static route
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Routers include karo
app.include_router(auth.router)
app.include_router(video.router)
app.include_router(dashboard.router)
app.include_router(transcript.router)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "ClipMind AI backend is running."}
