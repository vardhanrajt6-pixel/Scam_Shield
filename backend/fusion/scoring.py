def calculate_confidence(scores: dict) -> float:
    """
    Calculate overall confidence score from multiple sources.
    Example:
        scores = {"llm": 0.9, "virustotal": 0.8, "graph": 0.7}
    Returns a rounded confidence value.
    """
    if not scores:
        return 0.0

    # Average of provided scores
    confidence = sum(scores.values()) / len(scores)
    return round(confidence, 2)
