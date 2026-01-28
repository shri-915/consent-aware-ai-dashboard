"""
Text similarity utilities for evaluating AI output differences.

Implements cosine similarity and token-based overlap for comparing outputs.
"""
import math
import re
from collections import Counter
from typing import List


def tokenize(text: str) -> List[str]:
    """Simple tokenization (split on whitespace and punctuation)."""
    # Convert to lowercase and split on non-word characters
    tokens = re.findall(r"\b\w+\b", text.lower())
    return tokens


def cosine_similarity(text1: str, text2: str) -> float:
    """Compute cosine similarity between two text strings.

    Args:
        text1: First text string
        text2: Second text string

    Returns:
        Similarity score between 0.0 and 1.0
    """
    tokens1 = tokenize(text1)
    tokens2 = tokenize(text2)

    if not tokens1 or not tokens2:
        return 0.0

    # Create vocabulary and vectors
    all_tokens = set(tokens1 + tokens2)
    vec1 = Counter(tokens1)
    vec2 = Counter(tokens2)

    # Compute dot product and magnitudes
    dot_product = sum(vec1.get(token, 0) * vec2.get(token, 0) for token in all_tokens)
    magnitude1 = math.sqrt(sum(vec1.get(token, 0) ** 2 for token in all_tokens))
    magnitude2 = math.sqrt(sum(vec2.get(token, 0) ** 2 for token in all_tokens))

    if magnitude1 == 0.0 or magnitude2 == 0.0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)


def token_overlap(text1: str, text2: str) -> float:
    """Compute token overlap ratio between two texts.

    Args:
        text1: First text string
        text2: Second text string

    Returns:
        Overlap ratio between 0.0 and 1.0 (Jaccard-like similarity)
    """
    set1 = set(tokenize(text1))
    set2 = set(tokenize(text2))

    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0

    intersection = len(set1 & set2)
    union = len(set1 | set2)

    return intersection / union if union > 0 else 0.0


def compute_similarity(text1: str, text2: str) -> float:
    """Compute overall similarity using cosine similarity.

    This is the primary similarity function used for evaluation.
    """
    return cosine_similarity(text1, text2)
