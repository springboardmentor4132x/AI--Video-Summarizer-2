from app.services.analysis import analyze_transcript, chunk_transcript


def test_chunking_preserves_timing_and_source_boundaries() -> None:
    chunks = chunk_transcript([
        {"start": 0, "end": 4, "text": "Machine learning uses data."},
        {"start": 4, "end": 8, "text": "Models learn patterns."},
        {"start": 8, "end": 12, "text": "The weather is pleasant today."},
    ], max_chars=60)

    assert chunks[0]["start"] == 0
    assert chunks[0]["end"] == 8
    assert chunks[1]["start"] == 8


def test_analysis_creates_topics_and_deduplicates_overlapping_highlights() -> None:
    segments = [
        {"start": 0, "end": 10, "text": "Definition: machine learning uses data and models to learn patterns."},
        {"start": 2, "end": 8, "text": "An important example shows how models learn patterns from data."},
        {"start": 21, "end": 32, "text": "Finally, the conclusion is that weather forecasts need different inputs."},
    ]

    result = analyze_transcript(segments, max_chars=80, boundary_threshold=0.3)

    assert len(result["topics"]) == 2
    assert result["highlights"]
    assert len(result["highlights"]) == 2
    assert result["highlights"][0]["topic_index"] == 1
    assert result["highlights"][1]["topic_index"] == 2
