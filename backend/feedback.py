from functools import lru_cache
# FIXED: Changed 'from engine.utils' to 'from utils'
from utils import load_pickle_cache

FEEDBACK_CACHE = load_pickle_cache('feedback_cache.pkl')

@lru_cache(maxsize=None)
def _calculate_feedback(guess: str, secret: str) -> str:
    """The original, calculating version of the feedback logic."""
    feedback = ['b'] * 5
    secret_list = list(secret)
    guess_list = list(guess)

    for i in range(5):
        if guess_list[i] == secret_list[i]:
            feedback[i] = 'g'
            secret_list[i] = None
            guess_list[i] = None

    for i in range(5):
        if guess_list[i] is not None and guess_list[i] in secret_list:
            feedback[i] = 'y'
            secret_list[secret_list.index(guess_list[i])] = None

    return "".join(feedback)

def get_feedback(guess: str, secret: str) -> str:
    """
    This public function provides feedback. If the main cache is loaded,
    it performs an instant lookup. If not, it calculates the result.
    """
    if FEEDBACK_CACHE:
        try:
            return FEEDBACK_CACHE[guess][secret]
        except KeyError:
            # Fallback for words not in the pre-computed cache
            return _calculate_feedback(guess, secret)
    else:
        # Fallback if the cache file doesn't exist at all
        return _calculate_feedback(guess, secret)
