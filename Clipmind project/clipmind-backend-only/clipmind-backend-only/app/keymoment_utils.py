"""
keymoment_utils.py
-------------------
Module 3 ka core logic:
1. Transcript segments ko chunk karna
2. Embeddings generate karna (Sentence Transformers)
3. Neighboring chunks ke beech cosine similarity
4. Similarity drop se topic boundaries nikalna
5. Har segment ko importance score dena
6. Top segments ko key moments banana (overlap merge karke)
"""

import re
from typing import List, Dict

import numpy as np
from sentence_transformers import SentenceTransformer

_model = None


def get_model():
    """Model ek hi baar load hota hai (memory/time bachane ke liye)."""
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def chunk_segments(raw_segments: List[Dict], max_chunk_seconds: int = 20) -> List[Dict]:
    """
    Whisper se chhote-chhote segments (2-5 second ke) aate hain.
    Unhe milakar bade, meaningful chunks banate hain (~max_chunk_seconds tak),
    lekin sentence ke beech mein nahi todte.
    """
    if not raw_segments:
        return []

    chunks = []
    current_text = ""
    current_start = raw_segments[0]["start"]
    current_end = raw_segments[0]["start"]

    for seg in raw_segments:
        current_text += " " + seg["text"].strip()
        current_end = seg["end"]

        ends_sentence = bool(re.search(r"[.!?]\s*$", seg["text"].strip()))
        duration_ok = (current_end - current_start) >= max_chunk_seconds

        if ends_sentence and duration_ok:
            chunks.append({
                "start": int(current_start),
                "end": int(current_end),
                "text": current_text.strip(),
            })
            current_text = ""
            current_start = current_end

    if current_text.strip():
        chunks.append({
            "start": int(current_start),
            "end": int(current_end),
            "text": current_text.strip(),
        })

    return chunks


def generate_embeddings(chunks: List[Dict]) -> np.ndarray:
    model = get_model()
    texts = [c["text"] for c in chunks]
    return model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))  # already normalized, so dot product = cosine similarity


def detect_topic_boundaries(chunks: List[Dict], embeddings: np.ndarray, drop_threshold: float = 0.35) -> List[int]:
    """
    Neighboring chunks ke beech similarity dekh kar boundary indices return karta hai.
    Jahan similarity achanak drop hoti hai (threshold se zyada), wahan naya topic maana jaata hai.
    """
    boundaries = [0]  # pehla chunk hamesha ek topic ka start hai
    for i in range(1, len(chunks)):
        sim = cosine_sim(embeddings[i - 1], embeddings[i])
        if (1 - sim) > drop_threshold:
            boundaries.append(i)
    return boundaries


def build_topics(chunks: List[Dict], boundaries: List[int]) -> List[Dict]:
    topics = []
    for idx, start_idx in enumerate(boundaries):
        end_idx = boundaries[idx + 1] - 1 if idx + 1 < len(boundaries) else len(chunks) - 1
        title = chunks[start_idx]["text"].split(".")[0][:60]  # pehla sentence ko title bana diya (simple heuristic)
        topics.append({
            "title": title.strip() or f"Topic {idx + 1}",
            "start_time": chunks[start_idx]["start"],
            "end_time": chunks[end_idx]["end"],
        })
    return topics


def score_importance(chunk: Dict, position_index: int, total_chunks: int) -> float:
    """
    Simple weighted scoring:
    - length/content density (zyada content wale chunks thoda upar)
    - position (beech ke portions ko thoda zyada weight, intro/outro ko kam)
    Formula documented: 0.6 * density_score + 0.4 * position_score
    """
    density_score = min(len(chunk["text"]) / 400, 1.0)  # 400 chars ~ full score

    relative_pos = position_index / max(total_chunks - 1, 1)
    position_score = 1.0 - abs(relative_pos - 0.5) * 1.2  # middle segments ko halka boost
    position_score = max(position_score, 0.2)

    score = round(0.6 * density_score + 0.4 * position_score, 2)
    return min(score, 1.0)


def merge_overlapping(moments: List[Dict]) -> List[Dict]:
    """Time-overlap karte hue moments ko ek mein merge karta hai (jo zyada score wala hai use rakhta hai)."""
    if not moments:
        return []
    moments = sorted(moments, key=lambda m: m["start_time"])
    merged = [moments[0]]

    for m in moments[1:]:
        last = merged[-1]
        if m["start_time"] <= last["end_time"]:  # overlap
            if m["importance_score"] > last["importance_score"]:
                merged[-1] = m
        else:
            merged.append(m)

    return merged


def detect_key_moments(raw_segments: List[Dict], top_n: int = 5) -> Dict:
    """
    Main entry point. raw_segments = Whisper ka output [{"start","end","text"}, ...]
    Return: {"topics": [...], "key_moments": [...]}
    """
    chunks = chunk_segments(raw_segments)
    if not chunks:
        return {"topics": [], "key_moments": []}

    embeddings = generate_embeddings(chunks)
    boundaries = detect_topic_boundaries(chunks, embeddings)
    topics = build_topics(chunks, boundaries)

    scored = []
    for i, chunk in enumerate(chunks):
        score = score_importance(chunk, i, len(chunks))
        scored.append({
            "start_time": chunk["start"],
            "end_time": chunk["end"],
            "text": chunk["text"],
            "importance_score": score,
        })

    scored.sort(key=lambda x: x["importance_score"], reverse=True)
    top_moments = scored[:top_n]
    top_moments = merge_overlapping(top_moments)
    top_moments.sort(key=lambda x: x["start_time"])

    return {"topics": topics, "key_moments": top_moments}