from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re


# Load the embedding model once when the service starts
model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embeddings(texts: list[str]):
    """
    Convert transcript segments into numerical embeddings.
    """
    if not texts:
        return []

    return model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )


def calculate_similarity(embeddings):
    """
    Calculate cosine similarity between neighboring transcript segments.

    The last segment has no next segment, so its similarity is 0.0.
    """

    if len(embeddings) == 0:
        return []

    if len(embeddings) == 1:
        return [0.0]

    scores = []

    for i in range(len(embeddings)):
        if i == len(embeddings) - 1:
            scores.append(0.0)
            continue

        score = cosine_similarity(
            embeddings[i].reshape(1, -1),
            embeddings[i + 1].reshape(1, -1)
        )[0][0]

        # Keep similarity safely within 0-1
        score = max(0.0, min(float(score), 1.0))

        scores.append(round(score, 4))

    return scores


def calculate_importance(segments, similarity_scores):
    """
    Calculate an importance score for every transcript segment.

    Importance is based on:
    1. Content length
    2. Important keywords
    3. Semantic novelty

    Final score:
        30% Length
        30% Keywords
        40% Novelty

    Returns scores between 0 and 1.
    """

    if not segments:
        return []

    importance_scores = []

    important_keywords = {
        "important",
        "key",
        "main",
        "remember",
        "note",
        "conclusion",
        "finally",
        "therefore",
        "because",
        "definition",
        "example",
        "first",
        "second",
        "third",
        "in conclusion",
        "important point"
    }

    for i, text in enumerate(segments):

        text_lower = text.lower().strip()

        # --------------------------------
        # 1. Content Length Score
        # --------------------------------

        words = re.findall(r"\b\w+\b", text_lower)

        # Normalize around 30 words
        length_score = min(len(words) / 30.0, 1.0)

        # --------------------------------
        # 2. Keyword Score
        # --------------------------------

        keyword_count = 0

        for keyword in important_keywords:

            if " " in keyword:
                # Phrase matching
                if keyword in text_lower:
                    keyword_count += 1
            else:
                # Whole-word matching
                if re.search(
                    rf"\b{re.escape(keyword)}\b",
                    text_lower
                ):
                    keyword_count += 1

        keyword_score = min(keyword_count / 3.0, 1.0)

        # --------------------------------
        # 3. Novelty Score
        # --------------------------------

        if i == len(segments) - 1:
            # Last segment has no next segment.
            # Don't artificially give it maximum novelty.
            novelty_score = 0.0
        else:
            similarity = similarity_scores[i]

            # Similarity is already between 0 and 1.
            novelty_score = 1.0 - similarity

        # --------------------------------
        # 4. Final Importance Score
        # --------------------------------

        importance = (
            0.30 * length_score
            + 0.30 * keyword_score
            + 0.40 * novelty_score
        )

        # Keep score between 0 and 1
        importance = max(0.0, min(float(importance), 1.0))

        importance_scores.append(
            round(importance, 4)
        )

    return importance_scores


def score_segments(segments):
    """
    Complete scoring pipeline.

    Transcript segments
            ↓
    Sentence Embeddings
            ↓
    Cosine Similarity
            ↓
    Importance Scoring

    Returns:

    [
        {
            "text": "...",
            "similarity_score": 0.75,
            "importance_score": 0.62
        }
    ]
    """

    if not segments:
        return []

    # Remove empty segments
    clean_segments = [
        segment.strip()
        for segment in segments
        if segment and segment.strip()
    ]

    if not clean_segments:
        return []

    # Step 1: Generate embeddings
    embeddings = generate_embeddings(clean_segments)

    # Step 2: Calculate similarity
    similarity_scores = calculate_similarity(embeddings)

    # Step 3: Calculate importance
    importance_scores = calculate_importance(
        clean_segments,
        similarity_scores
    )

    # Step 4: Build final result
    results = []

    for i, text in enumerate(clean_segments):

        results.append({
            "text": text,
            "similarity_score": similarity_scores[i],
            "importance_score": importance_scores[i]
        })

    return results