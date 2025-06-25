import json
import pickle
import math
import os
import requests
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

def download_and_load_pickle(url: str, local_path: str):
    """Downloads the pickle file from a URL if it doesn't exist locally, then loads it."""
    try:
        # Check if the file already exists in the server's filesystem
        if not os.path.exists(local_path):
            print(f"Cache file not found at '{local_path}'. Downloading from cloud storage...")
            response = requests.get(url, stream=True)
            response.raise_for_status() # Raise an exception for bad status codes
            
            with open(local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("Download complete.")

        # Now load the file from the local path
        with open(local_path, 'rb') as f:
            print(f"Successfully loaded cache: {local_path}")
            return pickle.load(f)

    except requests.exceptions.RequestException as e:
        print(f"Error downloading cache file: {e}")
        return None
    except Exception as e:
        print(f"Error loading pickle file: {e}")
        return None


# --- Data and Cache Loading ---
ALL_WORDS = load_wordlist('wordlist.txt')
STARTER_CACHE = []
try:
    with open('starter_cache.json', 'r') as f:
        STARTER_CACHE = json.load(f)
    print("Successfully loaded starter_cache.json")
except FileNotFoundError:
    print("Warning: 'starter_cache.json' not found.")

# **MODIFIED:** This now downloads the cache from the cloud storage URL
# The URL is retrieved from an environment variable for security and flexibility.
CACHE_URL = os.getenv("FEEDBACK_CACHE_URL", "https://pub-7ce171e567e44062a07a86763ab8c539.r2.dev/feedback_cache.pkl")
FEEDBACK_CACHE = None
if CACHE_URL:
    # Render provides a temporary disk that we can write to.
    FEEDBACK_CACHE = download_and_load_pickle(CACHE_URL, local_path="/tmp/feedback_cache.pkl")
else:
    print("Warning: FEEDBACK_CACHE_URL environment variable not set. Solver will be slow.")

# (The rest of the helper functions remain the same...)
@lru_cache(maxsize=None)
def _calculate_feedback(guess: str, secret: str) -> str:
    feedback, secret_list, guess_list = ['b'] * 5, list(secret), list(guess)
    for i in range(5):
        if guess_list[i] == secret_list[i]: feedback[i], secret_list[i], guess_list[i] = 'g', None, None
    for i in range(5):
        if guess_list[i] is not None and guess_list[i] in secret_list: feedback[i], secret_list[secret_list.index(guess_list[i])] = 'y', None
    return "".join(feedback)

def get_feedback(guess: str, secret: str) -> str:
    if FEEDBACK_CACHE:
        try: return FEEDBACK_CACHE[guess.upper()][secret.upper()]
        except KeyError: return _calculate_feedback(guess.upper(), secret.upper())
    else: return _calculate_feedback(guess.upper(), secret.upper())

def filter_candidates(candidates: List[str], guess: str, feedback: str) -> List[str]:
    return [word for word in candidates if get_feedback(guess, word) == feedback]

def calculate_expected_entropy(guess: str, candidates: List[str]) -> float:
    if not candidates: return 0.0
    feedback_counts = Counter(get_feedback(guess, word) for word in candidates)
    total_candidates, entropy = len(candidates), 0.0
    for count in feedback_counts.values():
        p = count / total_candidates
        if p > 0: entropy -= p * math.log2(p)
    return entropy

def get_ranked_suggestions(candidates: List[str]) -> List[str]:
    if not candidates: return []
    if len(candidates) == len(ALL_WORDS) and STARTER_CACHE: return [item['guess'] for item in STARTER_CACHE]
    suggestions, search_space = [], candidates if len(candidates) <= 30 else ALL_WORDS
    for guess in search_space: suggestions.append({'guess': guess, 'entropy': calculate_expected_entropy(guess, candidates)})
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

# **MODIFIED:** Added your specific Netlify URL to the origins list
origins = [
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "https://deluxe-bublanina-f995ed.netlify.app" # Your deployed frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/suggestions", response_model=SuggestionResponse)
def get_suggestions_endpoint(request: SuggestionRequest):
    candidates = ALL_WORDS.copy()
    for item in request.history:
        if item.guess and len(item.guess) == 5: candidates = filter_candidates(candidates, item.guess.upper(), item.feedback)
    return {"suggestions": get_ranked_suggestions(candidates)}

@app.get("/")
def read_root(): return {"status": "Wordle Solver API is running."}

