import math
import json
from collections import Counter
from typing import List

# FIXED: Changed 'from engine.feedback' to 'from feedback'
from feedback import get_feedback

def calculate_expected_entropy(guess: str, candidates: List[str]) -> float:
    """Calculates the expected information gain (entropy) for a given guess."""
    if not candidates:
        return 0.0
    
    feedback_counts = Counter(get_feedback(guess, word) for word in candidates)
    total_candidates = len(candidates)
    entropy = 0.0
    for count in feedback_counts.values():
        probability = count / total_candidates
        if probability > 0:
            entropy -= probability * math.log2(probability)
    return entropy

def get_ranked_suggestions(
    candidates: List[str],
    all_words: List[str],
    starter_cache: List[dict]
) -> List[str]:
    """
    Calculates entropy for possible guesses and returns a ranked list of suggestions.
    """
    if not candidates:
        return []

    # If it's the start of the game, use the pre-computed fast cache.
    if len(candidates) == len(all_words):
        return [item['guess'] for item in starter_cache]

    suggestions = []
    # Heuristic: If candidate list is small, only check those words for the next guess.
    search_space = candidates if len(candidates) <= 30 else all_words

    for guess in search_space:
        entropy = calculate_expected_entropy(guess, candidates)
        suggestions.append({'guess': guess, 'entropy': entropy})
    
    # Sort by entropy (highest first)
    suggestions.sort(key=lambda x: x['entropy'], reverse=True)
    
    # Return just the word from the top 20 suggestions
    return [item['guess'] for item in suggestions[:20]]
