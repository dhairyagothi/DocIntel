from rapidfuzz.fuzz import ratio


def text_similarity(left: str, right: str) -> float:
    return ratio(left.lower().replace("_", " "), right.lower().replace("_", " ")) / 100