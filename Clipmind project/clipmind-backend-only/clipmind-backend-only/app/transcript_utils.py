"""
transcript_utils.py
--------------------
Module 2 ka core logic:
1. Video se audio nikalna (ffmpeg)
2. Local Whisper model se audio ko text mein convert karna (timestamps ke saath)
3. Transcript se simple extractive summary banana (100% free, local, koi external
   AI API call nahi hoti — word-frequency based sentence scoring use hota hai)
"""

import re
import subprocess
from pathlib import Path
from collections import Counter
from typing import Dict, List

_whisper_model = None


def get_whisper_model():
    """Model ek hi baar load hota hai (memory/time bachane ke liye)."""
    global _whisper_model
    if _whisper_model is None:
        import whisper  # openai-whisper package
        # "base" model speed aur accuracy ke beech achha balance deta hai, CPU par bhi chal jaata hai.
        _whisper_model = whisper.load_model("base")
    return _whisper_model


def extract_audio(video_path: str, audio_path: str) -> bool:
    """ffmpeg se video ki audio ko .wav mein nikalta hai (Whisper ko yeh format chahiye)."""
    try:
        Path(audio_path).parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", video_path,
                "-vn",
                "-ac", "1",
                "-ar", "16000",
                audio_path,
            ],
            capture_output=True,
            text=True,
            timeout=900,
        )
        return result.returncode == 0
    except Exception:
        return False


def transcribe_audio(audio_path: str) -> Dict:
    """
    Local Whisper model se audio ko transcribe karta hai.
    Returns: {"full_text": str, "segments": [{"start": float, "end": float, "text": str}, ...]}
    """
    model = get_whisper_model()
    result = model.transcribe(audio_path)

    segments = [
        {
            "start": round(seg["start"], 2),
            "end": round(seg["end"], 2),
            "text": seg["text"].strip(),
        }
        for seg in result.get("segments", [])
    ]
    return {"full_text": result.get("text", "").strip(), "segments": segments}


# ---------- Simple, local, free extractive summarization (koi paid API nahi) ----------

_STOPWORDS = set("""
a an the is are was were be been being of to in on at for with and or but
this that these those it its as by from into your you i we our their his her
""".split())


def _sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def generate_summary(full_text: str, segments: List[Dict]) -> Dict:
    sentences = _sentences(full_text)
    if not sentences:
        return {"short_summary": "", "topics": []}

    words = re.findall(r"[a-zA-Z]+", full_text.lower())
    freq = Counter(w for w in words if w not in _STOPWORDS and len(w) > 2)

    def score(sentence):
        s_words = re.findall(r"[a-zA-Z]+", sentence.lower())
        if not s_words:
            return 0
        return sum(freq.get(w, 0) for w in s_words) / len(s_words)

    ranked = sorted(sentences, key=score, reverse=True)
    top_n = max(1, min(3, len(ranked)))
    top_sentences = set(ranked[:top_n])
    short_summary = " ".join(s for s in sentences if s in top_sentences)

    chunk_count = min(4, max(1, len(segments) // 5 or 1))
    chunk_size = max(1, len(segments) // chunk_count) if segments else 1
    topics = []
    for i in range(0, len(segments), chunk_size):
        chunk = segments[i:i + chunk_size]
        if not chunk:
            continue
        chunk_text = " ".join(s["text"] for s in chunk).strip()
        if chunk_text:
            topics.append({"start_time": chunk[0]["start"], "text": chunk_text})

    return {"short_summary": short_summary, "topics": topics}