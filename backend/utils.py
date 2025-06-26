import logging
from typing import List
import pickle

def load_wordlist(path: str) -> List[str]:
    """Loads a wordlist from a file, ensuring words are uppercase."""
    try:
        with open(path, 'r') as f:
            return [line.strip().upper() for line in f if len(line.strip()) == 5]
    except FileNotFoundError:
        print(f"Error: Wordlist file not found at '{path}'")
        return []

def setup_logging() -> None:
    """Configures the logging format and level."""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(message)s',
        datefmt='%H:%M:%S'
    )

def load_pickle_cache(path: str):
    """Loads a cache file created by pickle."""
    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        logging.error(f"Cache file not found at: {path}")
        logging.error("Please run 'precompute_cache.py' to generate caches.")
        return None
