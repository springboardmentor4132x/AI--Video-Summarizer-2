"""
main.py
--------
FastAPI application entrypoint.

Run with:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routes import auth_routes, video_routes


# Create database tables automatically if they do not exist
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="ClipMind AI - Backend",
    description="Backend API for ClipMind AI (Infosys SpringBoard project)",
    version="0.1.0",
)


# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register routers
app.include_router(auth_routes.router)
app.include_router(video_routes.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "message": "ClipMind AI backend is running"
    }