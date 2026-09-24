from pathlib import Path

from app.config import settings

_question_generator = None


def generate_learning_question(context: str) -> tuple[str, str] | None:
    """Generate one transcript-grounded question and hint with a local HF model."""
    global _question_generator
    try:
        from transformers import pipeline

        if _question_generator is None:
            _question_generator = pipeline("text2text-generation", model=settings.question_model)
        question_prompt = (
            "Based only on this transcript passage, write one concise comprehension question "
            "about its most important fact or concept. Do not answer the question.\nPassage:\n"
            f"{context}"
        )
        question = _question_generator(question_prompt, max_new_tokens=64, do_sample=False)[0]["generated_text"].strip()
        hint_prompt = (
            "Write one short hint for the learner answering this question. Point to relevant "
            "keywords or relationships in the passage, but do not reveal the answer.\n"
            f"Question: {question}\nPassage:\n{context}"
        )
        hint = _question_generator(hint_prompt, max_new_tokens=64, do_sample=False)[0]["generated_text"].strip()
        question = question.removeprefix("Question:").strip()
        hint = hint.removeprefix("Hint:").strip()
        if question and hint:
            return question, hint
    except Exception:
        return None
    return None


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