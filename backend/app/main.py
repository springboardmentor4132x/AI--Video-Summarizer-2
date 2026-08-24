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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routes import auth_routes

# Create database tables automatically if they do not exist
Base.metadata.create_all(bind=engine)

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


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "ClipMind AI backend is running"}