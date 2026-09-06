from pathlib import Path

from app.config import settings


def transcribe_audio(audio_path: Path) -> dict:
    try:
        import whisper
    except ImportError as exc:
        raise RuntimeError("Whisper is not installed. Install openai-whisper to transcribe videos.") from exc
    model = whisper.load_model(settings.whisper_model)
    result = model.transcribe(str(audio_path), fp16=False)
    return {
        "language": result.get("language"),
        "full_text": (result.get("text") or "").strip(),
        "segments": result.get("segments") or [],
    }


def summarize_text(text: str) -> tuple[str, str]:
    try:
        from transformers import pipeline
    except ImportError as exc:
        raise RuntimeError("Transformers is not installed. Install transformers and torch to summarize videos.") from exc
    summarizer = pipeline("summarization", model=settings.summarizer_model)
    words = text.split()
    chunks = [" ".join(words[index:index + 700]) for index in range(0, len(words), 700)]
    chunk_summaries = [summarizer(chunk, max_length=130, min_length=30, do_sample=False)[0]["summary_text"] for chunk in chunks if chunk]
    detailed = " ".join(chunk_summaries)
    short = summarizer(detailed[:3000], max_length=70, min_length=20, do_sample=False)[0]["summary_text"]
    return short.strip(), detailed.strip()