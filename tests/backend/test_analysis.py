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


def test_analysis_generates_ranked_questions_with_hints_only() -> None:
    result = analyze_transcript([
        {"start": 0, "end": 10, "text": "Definition: machine learning uses data and models to learn patterns."},
        {"start": 21, "end": 32, "text": "Finally, the conclusion is that weather forecasts need different inputs."},
    ], max_chars=80)

    assert result["questions"]
    assert all(question["hint"] for question in result["questions"])
    assert all("answer" not in question for question in result["questions"])
    assert all("machine learning uses data and models to learn patterns" not in question["question"] for question in result["questions"])
    assert len({question["question"] for question in result["questions"]}) == len(result["questions"])
    assert len({question["hint"] for question in result["questions"]}) == len(result["questions"])


def test_questions_and_hints_are_specific_for_repeated_process_sections() -> None:
    result = analyze_transcript([
        {"start": 0, "end": 10, "text": "First, the chef measures ingredients before mixing the batter."},
        {"start": 20, "end": 30, "text": "Next, the model compares ingredients and selects a recipe."},
        {"start": 40, "end": 50, "text": "Finally, the oven heats the batter and produces the final dish."},
    ], max_chars=60, boundary_threshold=0.9)

    questions = result["questions"]
    assert len(questions) == 3
    assert len({item["question"] for item in questions}) == 3
    assert all(any(term in item["question"] for term in ("chef", "model", "oven", "ingredients", "batter", "recipe", "dish")) for item in questions)
    assert all(any(term in item["hint"] for term in ("chef", "model", "oven", "ingredients", "batter", "recipe", "dish")) for item in questions)
