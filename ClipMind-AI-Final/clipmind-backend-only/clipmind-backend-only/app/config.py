"""
config.py
---------
Sabhi environment settings ek jagah par. .env file se values read karta hai.
Agar .env file nahi milti to safe defaults use hote hain (dev ke liye).
"""

import os
from dotenv import load_dotenv

load_dotenv()  # .env file load karo agar mojood hai

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./clipmind.db")

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "200"))
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

# Sirf yeh video formats allow honge
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
