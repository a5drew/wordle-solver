from typing import List
# FIXED: Changed 'from engine.feedback' to 'from feedback'
from feedback import get_feedback

def filter_candidates(candidates: List[str], guess: str, feedback: str) -> List[str]:
    """
    Filters a list of candidate words based on a guess and its feedback.
    """
    return [word for word in candidates if get_feedback(guess, word) == feedback]
