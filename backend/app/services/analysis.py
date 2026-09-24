"""Transcript chunking, topic segmentation, and highlight ranking."""

from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Callable
from typing import Any

_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in",
    "is", "it", "of", "on", "or", "that", "the", "this", "to", "we", "with",
}
_IMPORTANCE_WORDS = {
    "important", "key", "because", "therefore", "definition", "example", "result",
    "conclusion", "first", "second", "finally", "means", "called", "how", "why",
}
_QUESTION_CUES = {
    "definition", "defined", "means", "called", "how", "step", "steps", "first", "then",
    "next", "finally", "because", "why", "important", "reason", "example", "examples",
    "instance", "result", "therefore", "conclusion", "summary", "summarize",
}


def _words(text: str) -> set[str]:
    return {word for word in re.findall(r"[a-z0-9]+", text.lower()) if word not in _STOP_WORDS}


def _jaccard(left: str, right: str) -> float:
    left_words = _words(left)
    right_words = _words(right)
    if not left_words or not right_words:
        return 0.0
    return len(left_words & right_words) / len(left_words | right_words)


def chunk_transcript(segments: list[dict[str, Any]], max_chars: int = 900) -> list[dict[str, Any]]:
    """Combine timed transcript segments without splitting source segments."""
    chunks: list[dict[str, Any]] = []
    current: list[dict[str, Any]] = []
    current_length = 0
    for source in segments:
        text = str(source.get("text") or "").strip()
        if not text:
            continue
        item = {"start": float(source.get("start", 0)), "end": float(source.get("end", source.get("start", 0))), "text": text}
        if current and current_length + len(text) + 1 > max_chars:
            chunks.append(_make_chunk(current))
            current = []
            current_length = 0
        current.append(item)
        current_length += len(text) + 1
    if current:
        chunks.append(_make_chunk(current))
    return chunks


def _make_chunk(items: list[dict[str, Any]]) -> dict[str, Any]:
    text = " ".join(item["text"] for item in items).strip()
    return {"start": items[0]["start"], "end": items[-1]["end"], "text": text}


def _embedding_similarities(chunks: list[dict[str, Any]]) -> list[float] | None:
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        return None
    model = SentenceTransformer("all-MiniLM-L6-v2")
    vectors = model.encode([chunk["text"] for chunk in chunks], normalize_embeddings=True)
    return [max(-1.0, min(1.0, float(sum(a * b for a, b in zip(vectors[index - 1], vectors[index]))))) for index in range(1, len(vectors))]


def _similarities(chunks: list[dict[str, Any]]) -> list[float]:
    if len(chunks) < 2:
        return []
    try:
        similarities = _embedding_similarities(chunks)
    except Exception:
        similarities = None
    if similarities is not None:
        return similarities
    return [_jaccard(chunks[index - 1]["text"], chunks[index]["text"]) for index in range(1, len(chunks))]


def _topic_ranges(chunks: list[dict[str, Any]], similarities: list[float], boundary_threshold: float) -> list[tuple[int, int]]:
    if not chunks:
        return []
    boundaries = {index for index, similarity in enumerate(similarities, start=1) if similarity < boundary_threshold}
    starts = [0, *sorted(boundaries)]
    return [(start, (starts[position + 1] if position + 1 < len(starts) else len(chunks)) - 1) for position, start in enumerate(starts)]


def _topic_title(text: str) -> str:
    sentence = _SENTENCE_END.split(text.strip(), maxsplit=1)[0]
    return sentence[:96].strip() or "Untitled topic"


def _importance(chunk: dict[str, Any], index: int, total: int) -> float:
    words = _words(chunk["text"])
    density = min(len(words) / 45, 1.0)
    keyword_signal = min(sum(word in _IMPORTANCE_WORDS for word in words) / 3, 1.0)
    position_signal = 1.0 if index in (0, total - 1) else 0.0
    return round(min(1.0, 0.55 * density + 0.3 * keyword_signal + 0.15 * position_signal), 4)


def _overlaps(left: dict[str, Any], right: dict[str, Any]) -> bool:
    intersection = max(0.0, min(left["end"], right["end"]) - max(left["start"], right["start"]))
    shorter = min(left["end"] - left["start"], right["end"] - right["start"])
    return shorter > 0 and intersection / shorter >= 0.5


def _question_anchor(text: str) -> str:
    words = [word for word in re.findall(r"[a-z][a-z0-9'-]+", text.lower()) if word not in _STOP_WORDS and word not in _QUESTION_CUES]
    unique_words = list(dict.fromkeys(words))
    return " ".join(unique_words[:4]) or "the main idea"


def _question_prompt(text: str, question_index: int) -> tuple[str, str]:
    lowered = text.lower()
    anchor = _question_anchor(text)
    if any(marker in lowered for marker in ("definition", "defined as", "means", "called")):
        prompts = [
            (f"How does the video define \"{anchor}\"?", f"Listen for the characteristics used to define \"{anchor}\"."),
            (f"What makes \"{anchor}\" different from related ideas?", f"Compare the description of \"{anchor}\" with the contrast made in the video."),
        ]
        return prompts[question_index % len(prompts)]
    if any(marker in lowered for marker in ("how", "step", "first", "then", "next", "finally")):
        prompts = [
            (f"What are the main steps in the process involving \"{anchor}\"?", f"Recall what happens first, what follows, and how the process ends for \"{anchor}\"."),
            (f"What changes as the process involving \"{anchor}\" moves forward?", f"Track the input, action, and result described for \"{anchor}\"."),
            (f"Why does the video use this process for \"{anchor}\"?", f"Focus on the purpose of the steps, not only their order, for \"{anchor}\"."),
        ]
        return prompts[question_index % len(prompts)]
    if any(marker in lowered for marker in ("because", "why", "important", "reason")):
        prompts = [
            (f"Why does the video say \"{anchor}\" matters?", f"Look for the reason the speaker gives for the importance of \"{anchor}\"."),
            (f"What problem does \"{anchor}\" help explain or solve?", f"Connect \"{anchor}\" to the problem or consequence mentioned in the explanation."),
        ]
        return prompts[question_index % len(prompts)]
    if "example" in lowered or "for instance" in lowered:
        prompts = [
            (f"What idea does the example about \"{anchor}\" illustrate?", f"Look past the details of the example and identify what \"{anchor}\" is meant to show."),
            (f"How does the example clarify \"{anchor}\"?", f"Use the example's outcome to explain the role of \"{anchor}\"."),
        ]
        return prompts[question_index % len(prompts)]
    if any(marker in lowered for marker in ("result", "therefore", "conclusion", "in summary")):
        prompts = [
            (f"What result does the video connect to \"{anchor}\"?", f"Listen for the outcome linked to \"{anchor}\" and the reasoning that leads to it."),
            (f"What conclusion should a learner draw about \"{anchor}\"?", f"Review the evidence before the conclusion and connect it to \"{anchor}\"."),
        ]
        return prompts[question_index % len(prompts)]
    prompts = [
        (
            f"What central claim does the video make about \"{anchor}\", and how is it supported?",
            f"Identify the claim about \"{anchor}\", then recall the explanation or evidence that follows it.",
        ),
        (
            f"How does \"{anchor}\" connect to the main subject of the video?",
            f"Use the transition into this section and the repeated terms that explain \"{anchor}\".",
        ),
    ]
    question, hint = prompts[question_index % len(prompts)]
    return question, hint


def generate_learning_questions(scored_chunks: list[dict[str, Any]], max_questions: int = 5) -> list[dict[str, Any]]:
    """Create recall prompts from the highest-value transcript chunks without answers."""
    questions: list[dict[str, Any]] = []
    selected: list[dict[str, Any]] = []
    for question_index, chunk in enumerate(sorted(scored_chunks, key=lambda item: item["score"], reverse=True)):
        if any(_overlaps(chunk, existing) for existing in selected):
            continue
        question, hint = _question_prompt(chunk["text"], question_index)
        if any(item["question"] == question for item in questions):
            question = f"What new point about {_question_anchor(chunk['text'])} should a learner remember?"
            hint = f"Review the explanation around {_question_anchor(chunk['text'])} and identify the point that was added here."
        questions.append({
            "start": chunk["start"],
            "end": chunk["end"],
            "topic_index": chunk["topic_index"],
            "question": question,
            "hint": hint,
            "score": chunk["score"],
        })
        selected.append(chunk)
        if len(questions) == max_questions:
            break
    return sorted(questions, key=lambda item: item["start"])


def generate_learning_questions_with_model(
    scored_chunks: list[dict[str, Any]],
    generator: Callable[[str], tuple[str, str] | None],
    max_questions: int = 5,
) -> list[dict[str, Any]]:
    """Prefer model-generated prompts while retaining deterministic fallback behavior."""
    questions: list[dict[str, Any]] = []
    selected: list[dict[str, Any]] = []
    for chunk in sorted(scored_chunks, key=lambda item: item["score"], reverse=True):
        if any(_overlaps(chunk, existing) for existing in selected):
            continue
        generated = generator(chunk["text"])
        if generated is None:
            fallback = generate_learning_questions([chunk], max_questions=1)
            question, hint = fallback[0]["question"], fallback[0]["hint"]
        else:
            question, hint = generated
        if any(item["question"].casefold() == question.casefold() for item in questions):
            continue
        questions.append({
            "start": chunk["start"],
            "end": chunk["end"],
            "topic_index": chunk["topic_index"],
            "question": question,
            "hint": hint,
            "score": chunk["score"],
        })
        selected.append(chunk)
        if len(questions) == max_questions:
            break
    return sorted(questions, key=lambda item: item["start"])


def analyze_transcript(
    segments: list[dict[str, Any]],
    *,
    max_chars: int = 900,
    boundary_threshold: float = 0.22,
    max_highlights: int = 8,
    question_generator: Callable[[str], tuple[str, str] | None] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    chunks = chunk_transcript(segments, max_chars=max_chars)
    similarities = _similarities(chunks)
    topics: list[dict[str, Any]] = []
    scored: list[dict[str, Any]] = []
    for topic_index, (start_index, end_index) in enumerate(_topic_ranges(chunks, similarities, boundary_threshold), start=1):
        topic_chunks = chunks[start_index:end_index + 1]
        topic = {
            "index": topic_index,
            "start": topic_chunks[0]["start"],
            "end": topic_chunks[-1]["end"],
            "title": _topic_title(topic_chunks[0]["text"]),
            "text": " ".join(chunk["text"] for chunk in topic_chunks),
        }
        topics.append(topic)
        for chunk_index, chunk in enumerate(topic_chunks, start=start_index):
            scored.append({**chunk, "topic_index": topic_index, "score": _importance(chunk, chunk_index, len(chunks))})
    selected: list[dict[str, Any]] = []
    for candidate in sorted(scored, key=lambda item: item["score"], reverse=True):
        if any(_overlaps(candidate, existing) for existing in selected):
            continue
        selected.append(candidate)
        if len(selected) == max_highlights:
            break
    selected.sort(key=lambda item: item["start"])
    questions = generate_learning_questions_with_model(scored, question_generator) if question_generator else generate_learning_questions(scored)
    return {"topics": topics, "highlights": selected, "questions": questions}
