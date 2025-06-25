# engine/filter.py
from typing import List
from engine.feedback import get_feedback

def filter_candidates(candidates: List[str], guess: str, feedback: str) -> List[str]:
    """
    Filters a list of candidate words based on a guess and its feedback.

    Returns a new list containing only the words that, if they were the
    secret word, would produce the given feedback for the given guess.
    """
    return [word for word in candidates if get_feedback(guess, word) == feedback]

# This block lets us test the file directly
if __name__ == '__main__':
    print("--- Testing Filter Logic ---")
    candidates = ["CRANE", "CRAVE", "SLATE", "SHAKE", "TRACE"]
    guess = "SLATE"
    secret = "CRANE"

    # Get the actual feedback for a known secret
    actual_feedback = get_feedback(guess, secret)
    print(f"If secret is '{secret}', the feedback for '{guess}' is '{actual_feedback}'")

    remaining_words = filter_candidates(candidates, guess, actual_feedback)
    print(f"Original candidates: {candidates}")
    print(f"Remaining candidates after filtering: {remaining_words}")
    print(f"Expected remaining: ['CRANE']")