import re

_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in",
    "is", "it", "of", "on", "or", "that", "the", "this", "to", "we", "with",
}

_QUESTION_CUES = {
    "definition", "defined", "means", "called", "how", "step", "steps", "first", "then",
    "next", "finally", "because", "why", "important", "reason", "example", "examples",
    "instance", "result", "therefore", "conclusion", "summary", "summarize",
}

def _question_anchor(text: str) -> str:
    words = [word for word in re.findall(r"[a-z][a-z0-9'-]+", text.lower()) if word not in _STOP_WORDS and word not in _QUESTION_CUES]
    unique_words = list(dict.fromkeys(words))
    # Utkarsh's original code blindly took the first 4 words. Let's just take the first 2-3 to make it sound like a subject, or fallback.
    return " ".join(unique_words[:2]) or "the main concept"

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

def generate_questions_for_chunks(key_moment_chunks) -> list[dict]:
    questions = []
    for i, chunk in enumerate(key_moment_chunks):
        q, h = _question_prompt(chunk["transcript_text"], i)
        questions.append({
            "id": chunk["id"],
            "start_sec": chunk["start_sec"],
            "end_sec": chunk["end_sec"],
            "question": q,
            "hint": h
        })
    return questions
