from app.services.scoring_service import score_segments


segments = [
    "Machine learning is a branch of artificial intelligence.",

    "Machine learning uses data to learn patterns and make predictions.",

    "An important point is that machine learning can be used for classification and regression.",

    "The weather today is very pleasant.",

    "In conclusion, machine learning helps computers learn from data without being explicitly programmed."
]


results = score_segments(segments)


for result in results:

    print("\n----------------------------------")
    print(f"Text: {result['text']}")
    print(f"Similarity Score: {result['similarity_score']}")
    print(f"Importance Score: {result['importance_score']}")