import json
import math
import os
import requests
import zipfile
import io
from collections import Counter
from typing import List, Dict, Optional
from functools import lru_cache
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from joblib import load

# --- All Logic Consolidated into One File ---

# Section 1: Cache Loading and Management
# ========================================

@lru_cache(maxsize=None)
def _calculate_feedback(guess: str, secret: str) -> str:
    """Calculates feedback dynamically if a word is not in the cache."""
    guess, secret = guess.upper(), secret.upper()
    feedback, secret_list, guess_list = ['b'] * 5, list(secret), list(guess)
    for i in range(5):
        if guess_list[i] == secret_list[i]: feedback[i], secret_list[i], guess_list[i] = 'g', None, None
    for i in range(5):
        if guess_list[i] is not None and guess_list[i] in secret_list: feedback[i], secret_list[secret_list.index(guess_list[i])] = 'y', None
    return "".join(feedback)

class FeedbackCache:
    """A lazy-loading cache for Wordle feedback."""
    def __init__(self, cache_dir: str):
        self.cache_dir = cache_dir
        self._loaded_guesses: Dict[str, Dict[str, str]] = {}
        if not os.path.exists(cache_dir):
            print(f"Warning: Cache directory '{cache_dir}' not found. All feedback will be calculated dynamically.")

    def _load_guess_file(self, guess: str) -> Optional[Dict[str, str]]:
        """Loads a single .joblib file into memory."""
        file_path = os.path.join(self.cache_dir, f"{guess.lower()}.joblib")
        if os.path.exists(file_path):
            try: return load(file_path)
            except Exception as e: print(f"Error loading cache file '{file_path}': {e}"); return None
        return None

    def get_feedback(self, guess: str, answer: str) -> str:
        guess_upper, answer_upper = guess.upper(), answer.upper()
        if guess_upper not in self._loaded_guesses:
            self._loaded_guesses[guess_upper] = self._load_guess_file(guess_upper) or {}
        return self._loaded_guesses[guess_upper].get(answer_upper) or _calculate_feedback(guess_upper, answer_upper)

# Section 2: Application Startup Logic (Lifespan)
# =================================================

app_state = {}

def extract_local_zip(zip_path: str, extract_to: str):
    """Extracts a local ZIP file to a specified directory."""
    if not os.path.exists(zip_path):
        print(f"Error: Local cache ZIP file not found at '{zip_path}'. Solver will be slow.")
        return

    if os.path.exists(extract_to) and os.listdir(extract_to):
        print(f"Cache directory '{extract_to}' already exists. Skipping extraction.")
        return

    print(f"Extracting local cache from {zip_path}...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            os.makedirs(extract_to, exist_ok=True)
            z.extractall(extract_to)
        print(f"Cache successfully extracted to '{extract_to}'.")
    except Exception as e:
        print(f"An unexpected error occurred during local extraction: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup logic."""
    print("Application startup...")
    
    # **MODIFIED:** This now looks for the 'cache_split.zip' file within the project directory.
    current_dir = os.path.dirname(__file__)
    local_zip_path = os.path.join(current_dir, "cache_split.zip")
    
    # Use a temporary directory that works on both Windows and Linux/Render
    cache_base_dir = os.path.join(os.path.expanduser("~"), "tmp", "wordle_cache")
    
    extract_local_zip(local_zip_path, cache_base_dir)
    
    app_state["feedback_cache"] = FeedbackCache(cache_dir=cache_base_dir)
    yield
    print("Application shutdown...")
    app_state.clear()

# Section 3: FastAPI Application and Endpoints
# ============================================

app = FastAPI(lifespan=lifespan)

# --- Static Data Loading ---
def load_wordlist(path: str) -> List[str]:
    try:
        with open(path, 'r') as f: return [line.strip().upper() for line in f if len(line.strip()) == 5]
    except FileNotFoundError: print(f"FATAL ERROR: 'wordlist.txt' not found at '{path}'"); return []
ALL_WORDS = load_wordlist('wordlist.txt')
STARTER_CACHE = []
try:
    with open('starter_cache.json', 'r') as f: STARTER_CACHE = json.load(f)
    print("Successfully loaded starter_cache.json")
except FileNotFoundError: print("Warning: 'starter_cache.json' not found.")

# --- Solver Functions ---
def filter_candidates(candidates: List[str], guess: str, feedback: str) -> List[str]:
    cache = app_state.get("feedback_cache")
    return [word for word in candidates if cache.get_feedback(guess, word) == feedback]

def calculate_expected_entropy(guess: str, candidates: List[str]) -> float:
    if not candidates: return 0.0
    cache = app_state.get("feedback_cache")
    feedback_counts = Counter(cache.get_feedback(guess, word) for word in candidates)
    total_candidates, entropy = len(candidates), 0.0
    for count in feedback_counts.values():
        p = count / total_candidates
        if p > 0: entropy -= p * math.log2(p)
    return entropy

def get_ranked_suggestions(candidates: List[str]) -> List[str]:
    if not candidates: return []
    if len(candidates) == len(ALL_WORDS) and STARTER_CACHE:
        print("Using starter cache for initial suggestion.")
        return [item['guess'] for item in STARTER_CACHE]
    
    print(f"Calculating suggestions for {len(candidates)} candidates.")
    suggestions, search_space = [], candidates if len(candidates) <= 30 else ALL_WORDS
    for guess in search_space:
        entropy = calculate_expected_entropy(guess, candidates)
        suggestions.append({'guess': guess, 'entropy': entropy})
    suggestions.sort(key=lambda x: x['entropy'], reverse=True)
    return [item['guess'] for item in suggestions[:20]]

# --- API Data Models ---
class GuessHistory(BaseModel):
    guess: str; feedback: str
class SuggestionRequest(BaseModel):
    history: List[GuessHistory]
class SuggestionResponse(BaseModel):
    suggestions: List[str]

# --- CORS Middleware ---
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174,https://optimal-wordle.netlify.app").split(",")
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# --- API Endpoints ---
@app.post("/api/suggestions", response_model=SuggestionResponse)
def get_suggestions_endpoint(req: SuggestionRequest):
    candidates = ALL_WORDS.copy()
    for item in req.history:
        if item.guess and len(item.guess) == 5:
            candidates = filter_candidates(candidates, item.guess.upper(), item.feedback)
    ranked_list = get_ranked_suggestions(candidates)
    return {"suggestions": ranked_list}

@app.get("/")
def read_root():
    return {"status": "Wordle Solver API with Lazy-Loading Cache is running."}
