
"""
quiz_utils.py
--------------
Self-assessment (MCQ quiz) ka core logic: video ke transcript topics se
fill-in-the-blank style multiple-choice questions banata hai.
 
100% free aur local hai — sirf word-frequency analysis use hota hai,
koi internet ya paid AI API nahi chahiye (Module 2 ki summarization
jaisa hi approach).
"""
 
import random
import re
from collections import Counter
from typing import Dict, List
 
_STOPWORDS = set(
    """
    a an the is are was were be been being of to in on at for with and or but
    this that these those it its as by from into your you i we our their his her
    what when where who why how does do did can could should would will
    """.split()
)
 
 
def _keywords(text: str) -> List[str]:
    words = re.findall(r"[a-zA-Z]+", (text or "").lower())
    return [w for w in words if w not in _STOPWORDS and len(w) > 3]
 
 
def _top_keyword_in(text: str, global_freq: Counter):
    words = _keywords(text)
    if not words:
        return None
    scored = sorted(set(words), key=lambda w: global_freq.get(w, 0), reverse=True)
    return scored[0] if scored else None
 
 
def _sentence_with_word(text: str, word: str) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    for s in sentences:
        if re.search(rf"\b{re.escape(word)}\b", s, re.IGNORECASE):
            return s.strip()
    return text.strip()[:160]
 
 
def _blank_out(sentence: str, word: str) -> str:
    return re.sub(rf"\b{re.escape(word)}\b", "_____", sentence, count=1, flags=re.IGNORECASE)
 
 
def generate_quiz(full_text: str, topics: List[Dict], num_questions: int = 5) -> List[Dict]:
    """
    topics: [{"start_time": float, "text": str}, ...] (transcript_utils.generate_summary() ka output)
 
    Returns: [{
        "id", "question", "options": [{"id","text"}],
        "correct_option_id", "explanation", "topic", "start_time"
    }, ...]
    """
    words = re.findall(r"[a-zA-Z]+", (full_text or "").lower())
    global_freq = Counter(w for w in words if w not in _STOPWORDS and len(w) > 3)
 
    candidates = []
    for t in topics:
        chunk_text = t.get("text", "")
        keyword = _top_keyword_in(chunk_text, global_freq)
        if keyword:
            sentence = _sentence_with_word(chunk_text, keyword)
            candidates.append(
                {
                    "topic_label": chunk_text[:60] + ("…" if len(chunk_text) > 60 else ""),
                    "keyword": keyword,
                    "sentence": sentence,
                    "start_time": t.get("start_time", 0),
                }
            )
 
    if not candidates:
        return []
 
    random.shuffle(candidates)
    selected = candidates[:num_questions]
    all_keywords = list({c["keyword"] for c in candidates})
 
    questions = []
    for i, c in enumerate(selected):
        distractor_pool = [k for k in all_keywords if k != c["keyword"]]
        random.shuffle(distractor_pool)
        distractors = distractor_pool[:3]
        while len(distractors) < 3:
            # Bahut chhota video ho to fallback generic distractors
            distractors.append(f"topic{len(distractors) + 1}")
 
        options_words = distractors + [c["keyword"]]
        random.shuffle(options_words)
        options = [{"id": chr(97 + idx), "text": w} for idx, w in enumerate(options_words)]
        correct_id = next(o["id"] for o in options if o["text"] == c["keyword"])
 
        questions.append(
            {
                "id": f"q{i + 1}",
                "question": f'Video ke mutabik, blank mein kaunsa shabd sahi hoga?\n"{_blank_out(c["sentence"], c["keyword"])}"',
                "options": options,
                "correct_option_id": correct_id,
                "explanation": f'Sahi jawab "{c["keyword"]}" hai. Video mein yeh line thi: "{c["sentence"]}"',
                "topic": c["topic_label"],
                "start_time": c["start_time"],
            }
        )
 
    return questions
