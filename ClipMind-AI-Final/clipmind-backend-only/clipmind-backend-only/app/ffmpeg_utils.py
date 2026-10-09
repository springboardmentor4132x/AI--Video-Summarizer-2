"""
ffmpeg_utils.py
---------------
Module 1 ke liye "basic" FFmpeg pipeline. Iska kaam hai:
1. Video ki duration nikalna (ffprobe se)
2. Ek thumbnail image generate karna (ffmpeg se)

NOTE: Yeh function machine par ffmpeg/ffprobe installed hone ki
expect karta hai (`sudo apt install ffmpeg`). Agar ffmpeg installed
nahi hai to yeh gracefully fail ho jaata hai aur status "failed" set
ho jaata hai — poori app crash nahi hoti.

Agle modules mein isi jagah transcription, summarization, aur key-moment
detection ka code add hoga.
"""

import json
import subprocess
from pathlib import Path
from typing import Optional


def get_video_duration_seconds(file_path: str) -> Optional[int]:
    """ffprobe use karke video ki duration (seconds mein) nikalta hai."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "json",
                file_path,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        duration = float(data["format"]["duration"])
        return int(duration)
    except Exception:
        # ffmpeg not installed, corrupt file, timeout, etc.
        return None


def generate_thumbnail(file_path: str, output_path: str, timestamp: str = "00:00:01") -> bool:
    """Video ke ek frame se thumbnail (.jpg) banata hai."""
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i", file_path,
                "-ss", timestamp,
                "-vframes", "1",
                output_path,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode == 0
    except Exception:
        return False


def process_video(file_path: str, thumbnail_path: str) -> dict:
    """
    Poora basic processing pipeline chalata hai aur result return karta hai.
    Background task se call hota hai taki upload API turant response de sake.
    """
    duration = get_video_duration_seconds(file_path)
    thumbnail_ok = generate_thumbnail(file_path, thumbnail_path)

    return {
        "duration_seconds": duration,
        "thumbnail_generated": thumbnail_ok,
        "success": duration is not None,
    }
