"""
summarization_utils.py
Module 2 - AI Summarization (Short + Detailed) using BART
"""

from typing import List, Optional

MODEL_NAME = "facebook/bart-large-cnn"
_summarizer = None

WORDS_PER_CHUNK = 700


def _get_summarizer():
    global _summarizer
    if _summarizer is None:
        from transformers import pipeline
        _summarizer = pipeline("summarization", model=MODEL_NAME)
    return _summarizer


def chunk_text(text: str, words_per_chunk: int = WORDS_PER_CHUNK) -> List[str]:
    words = text.split()
    if not words:
        return []
    return [
        " ".join(words[i:i + words_per_chunk])
        for i in range(0, len(words), words_per_chunk)
    ]


def _summarize_text(text: str, max_length: int, min_length: int) -> Optional[str]:
    try:
        summarizer = _get_summarizer()
        word_count = len(text.split())
        safe_max = min(max_length, max(min_length + 10, word_count))
        result = summarizer(text, max_length=safe_max, min_length=min(min_length, safe_max - 1), do_sample=False)
        return result[0]["summary_text"].strip()
    except Exception:
        return None


def generate_summaries(transcript_text: str) -> dict:
    if not transcript_text or not transcript_text.strip():
        return {"success": False, "short_summary": None, "detailed_summary": None,
                "error": "Transcript text is empty."}

    chunks = chunk_text(transcript_text)
    chunk_summaries = []
    for chunk in chunks:
        summary = _summarize_text(chunk, max_length=180, min_length=40)
        if summary is None:
            return {"success": False, "short_summary": None, "detailed_summary": None,
                    "error": "Summarization model failed on one of the transcript chunks."}
        chunk_summaries.append(summary)

    if not chunk_summaries:
        return {"success": False, "short_summary": None, "detailed_summary": None,
                "error": "No content available to summarize."}

    detailed_summary = " ".join(chunk_summaries)

    short_summary = _summarize_text(detailed_summary, max_length=80, min_length=20)
    if short_summary is None:
        short_summary = detailed_summary[:300]

    return {
        "success": True,
        "short_summary": short_summary,
        "detailed_summary": detailed_summary,
        "error": None,
    }