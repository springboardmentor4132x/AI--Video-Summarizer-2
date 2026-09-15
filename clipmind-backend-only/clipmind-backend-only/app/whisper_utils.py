"""
whisper_utils.py
Module 2 - Transcript Generation (Video -> Audio -> Whisper -> Text)
"""

import subprocess
from pathlib import Path
from typing import Optional

_whisper_model = None


def _get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        import whisper
        _whisper_model = whisper.load_model("base")
    return _whisper_model


def extract_audio(video_path: str, audio_path: str) -> bool:
    try:
        Path(audio_path).parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", video_path,
                "-vn",
                "-acodec", "pcm_s16le",
                "-ar", "16000",
                "-ac", "1",
                audio_path,
            ],
            capture_output=True, text=True, timeout=600,
        )
        return result.returncode == 0 and Path(audio_path).exists()
    except Exception:
        return False


def transcribe_audio(audio_path: str) -> Optional[str]:
    try:
        model = _get_whisper_model()
        result = model.transcribe(audio_path)
        text = (result.get("text") or "").strip()
        return text if text else None
    except Exception:
        return None


def generate_transcript(video_path: str, audio_path: str) -> dict:
    audio_ok = extract_audio(video_path, audio_path)
    if not audio_ok:
        return {"success": False, "transcript_text": None, "error": "Audio extraction failed (FFmpeg)."}

    text = transcribe_audio(audio_path)
    if text is None:
        return {"success": False, "transcript_text": None, "error": "Whisper transcription failed."}

    return {"success": True, "transcript_text": text, "error": None}