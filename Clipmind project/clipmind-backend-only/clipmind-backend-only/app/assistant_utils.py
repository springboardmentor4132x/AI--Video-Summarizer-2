
"""
assistant_utils.py
--------------------
Module 4 ka core logic: AI Assistant chat box ke liye 100% free/local
keyword-matching based question answering (koi paid AI API call nahi hoti).
 
Transcript segments, summary topics aur key-moments ko context ki tarah
use karke user ke sawaal se sabse zyada milte-julte segments/moments
dhoondh kar jawab banata hai.
"""
 
import re
from collections import Counter
from typing import Dict, List
 
_STOPWORDS = set(
    """
    a an the is are was were be been being of to in on at for with and or but
    this that these those it its as by from into your you i we our their his her
    what when where who why how does do did can could should would tell me about
    """.split()
)
 
 
def _keywords(text: str) -> List[str]:
    words = re.findall(r"[a-zA-Z]+", (text or "").lower())
    return [w for w in words if w not in _STOPWORDS and len(w) > 2]
 
 
def _score_text(candidate: str, q_words: List[str], q_freq: Counter) -> float:
    c_words = _keywords(candidate)
    if not c_words:
        return 0.0
    return sum(q_freq.get(w, 0) for w in c_words) / len(c_words)
 
 
def _format_time(seconds) -> str:
    try:
        seconds = float(seconds)
    except (TypeError, ValueError):
        return "0:00"
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m}:{s:02d}"
 
 
def answer_question(question: str, context: Dict) -> Dict:
    """
    User ke sawaal ka jawab video ke transcript/summary/keymoments data
    (context) ke basis par local keyword-matching se deta hai.
 
    Returns:
        {
            "answer": str,
            "matched_segments": [{"start_time": float, "text": str}, ...]
        }
    """
    q_words = _keywords(question)
    q_freq = Counter(q_words)
 
    video_ctx = context.get("video", {}) or {}
    transcript_ctx = context.get("transcript", {}) or {}
    summary_ctx = context.get("summary", {}) or {}
    keymoments_ctx = context.get("keymoments", {}) or {}
 
    q_lower = (question or "").lower()
 
    # ---------- Direct intent shortcuts ----------
    if any(w in q_lower for w in ["summary", "summarize", "saransh"]):
        short_summary = summary_ctx.get("short_summary")
        if short_summary:
            return {"answer": short_summary, "matched_segments": []}
        return {
            "answer": "Is video ka summary abhi available nahi hai. Pehle transcript/summary generate karein.",
            "matched_segments": [],
        }
 
    if any(w in q_lower for w in ["how long", "duration", "kitni der", "length"]):
        duration = video_ctx.get("duration_seconds")
        if duration:
            return {
                "answer": f"Yeh video {_format_time(duration)} (mm:ss) lambi hai.",
                "matched_segments": [],
            }
        return {"answer": "Video ki duration abhi maloom nahi hai.", "matched_segments": []}
 
    if any(w in q_lower for w in ["key moment", "important moment", "highlight"]):
        moments = keymoments_ctx.get("key_moments", [])
        if moments:
            top = sorted(moments, key=lambda m: m.get("score", 0), reverse=True)[:3]
            lines = [f"- [{_format_time(m['start_time'])}] {m['text']}" for m in top]
            return {
                "answer": "Video ke top key moments:\n" + "\n".join(lines),
                "matched_segments": [
                    {"start_time": m["start_time"], "text": m["text"]} for m in top
                ],
            }
        return {"answer": "Is video ke liye key moments abhi generate nahi hue hain.", "matched_segments": []}
 
    # ---------- Fallback: search transcript segments for best keyword match ----------
    segments = transcript_ctx.get("segments") or []
    if not segments and not summary_ctx.get("topics"):
        return {
            "answer": "Is video ka transcript abhi ready nahi hai, is liye main sawaal ka jawab nahi de sakta.",
            "matched_segments": [],
        }
 
    if not q_words:
        return {
            "answer": "Kripya apna sawaal thoda specific likhein taaki main transcript mein sahi jawab dhoond sakoon.",
            "matched_segments": [],
        }
 
    scored = []
    for seg in segments:
        score = _score_text(seg.get("text", ""), q_words, q_freq)
        if score > 0:
            scored.append((score, seg))
 
    scored.sort(key=lambda x: x[0], reverse=True)
    top_matches = [seg for _, seg in scored[:3]]
 
    if top_matches:
        lines = [f"- [{_format_time(m['start'])}] {m['text']}" for m in top_matches]
        answer = "Mujhe transcript mein yeh related segments mile:\n" + "\n".join(lines)
        return {
            "answer": answer,
            "matched_segments": [
                {"start_time": m["start"], "text": m["text"]} for m in top_matches
            ],
        }
 
    return {
        "answer": "Maaf kijiye, is sawaal ka jawab mujhe is video ke transcript mein nahi mila.",
        "matched_segments": [],
    }
