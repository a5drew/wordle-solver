import json
import pickle
import math
from collections import Counter
from typing import List
from functools import lru_cache

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- All Helper Functions Consolidated Here ---

def load_wordlist(path: str) -> List[str]:
    """Loads a wordlist from a file, ensuring words are uppercase."""
    try:
        with open(path, 'r') as f:
            return [line.strip().upper() for line in f if len(line.strip()) == 5]
    except FileNotFoundError:
        print(f"FATAL ERROR: The essential 'wordlist.txt' file was not found at '{path}'")
        return []

def load_pickle_cache(path: str):
    """Loads a cache file created by pickle, using print for errors."""
    try:
        with open(path, 'rb') as f:
            print(f"Successfully loaded cache: {path}")
            return pickle.load(f)
    except FileNotFoundError:
        # Use print() because logging might not be configured at import time.
        print(f"Warning: Cache file not found at: {path}. The solver will be slower.")
        print("You can run a pre-computation script to generate this cache for a massive speed-up.")
        return None

# --- Data and Cache Loading ---
# This code runs once when the server starts.
ALL_WORDS = load_wordlist('wordlist.txt')
STARTER_CACHE = []
try:
    with open('starter_cache.json', 'r') as f:
        STARTER_CACHE = json.load(f)
    print("Successfully loaded starter_cache.json")
except FileNotFoundError:
    print("Warning: 'starter_cache.json' not found. Initial suggestions will be slower.")

# The feedback cache is essential for performance.
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
    """Provides feedback, using the cache if available."""
    if FEEDBACK_CACHE:
        try:
            return FEEDBACK_CACHE[guess.upper()][secret.upper()]
        except KeyError:
            return _calculate_feedback(guess.upper(), secret.upper())
    else:
        return _calculate_feedback(guess.upper(), secret.upper())

def filter_candidates(candidates: List[str], guess: str, feedback: str) -> List[str]:
    """Filters a list of candidate words based on a guess and its feedback."""
    return [word for word in candidates if get_feedback(guess, word) == feedback]

def calculate_expected_entropy(guess: str, candidates: List[str]) -> float:
    """Calculates the expected information gain (entropy) for a given guess."""
    if not candidates: return 0.0
    feedback_counts = Counter(get_feedback(guess, word) for word in candidates)
    total_candidates = len(candidates)
    entropy = 0.0
    for count in feedback_counts.values():
        probability = count / total_candidates
        if probability > 0: entropy -= probability * math.log2(probability)
    return entropy

def get_ranked_suggestions(candidates: List[str]) -> List[str]:
    """Calculates entropy and returns a ranked list of suggestions."""
    if not candidates: return []
    if len(candidates) == len(ALL_WORDS) and STARTER_CACHE:
        return [item['guess'] for item in STARTER_CACHE]

    suggestions = []
    search_space = candidates if len(candidates) <= 30 else ALL_WORDS
    for guess in search_space:
        entropy = calculate_expected_entropy(guess, candidates)
        suggestions.append({'guess': guess, 'entropy': entropy})
    
    suggestions.sort(key=lambda x: x['entropy'], reverse=True)
    return [item['guess'] for item in suggestions[:20]]

# --- API Data Models ---
class GuessHistory(BaseModel):
    guess: str
    feedback: str

class SuggestionRequest(BaseModel):
    history: List[GuessHistory]

class SuggestionResponse(BaseModel):
    suggestions: List[str]

# --- FastAPI Application ---
app = FastAPI()

# **FIX:** Added the correct frontend URL to the list of allowed origins.
origins = [
    "http://localhost:5174", # Vite's default port
    "http://127.0.0.1:5174",
    "https://deluxe-bublanina-f995ed.netlify.app/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

@app.post("/api/suggestions", response_model=SuggestionResponse)
def get_suggestions_endpoint(request: SuggestionRequest):
    candidates = ALL_WORDS.copy()
    for item in request.history:
        if item.guess and len(item.guess) == 5:
            candidates = filter_candidates(candidates, item.guess.upper(), item.feedback)
    
    ranked_list = get_ranked_suggestions(candidates)
    return {"suggestions": ranked_list}

@app.get("/")
def read_root():
    return {"status": "Wordle Solver API is running."}
