# ♟️ Information-Theoretic Wordle Solver

This is a full-stack, high-performance Wordle solving application that uses information theory to determine the optimal guess at every step. The frontend is built with React and Tailwind CSS, and the backend API is powered by Python and FastAPI.

**Live Demo:** [**wordle-solver-drew.netlify.app**](https://wordle-solver-drew.netlify.app/)

## Key Features

* **Optimal Guessing:** Implements information theory by calculating the **expected entropy** for over 3,000 words to find the guess that provides the most information.

* **High-Performance Backend:** A robust FastAPI server that handles the computationally intensive analysis.

* **Performance Caching:** Utilizes a pre-computed cache of all possible guess/answer feedback pairings (`feedback_cache.pkl`), reducing calculation time from minutes to milliseconds and optimizing API response time by over 99%.

* **Dynamic Frontend:** A beautiful and responsive single-page application built with React, Vite, and Framer Motion, providing a smooth user experience.

* **CI/CD Deployment:** The frontend is automatically deployed via Netlify and the backend via Render, ensuring seamless updates.

## Technology Stack

![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Render](https://img.shields.io/badge/Render-%46E3B7.svg?style=for-the-badge&logo=render&logoColor=white)
![Netlify](https://img.shields.io/badge/netlify-%23000000.svg?style=for-the-badge&logo=netlify&logoColor=#00C7B7)


## Local Development

To run this project on your local machine, follow these steps.

### Prerequisites

* Node.js (v18 or higher)

* Python 3.9 or higher

* Git

### 1. Clone the Repository

```
git clone [https://github.com/YourUsername/wordle-solver-fullstack.git](https://github.com/YourUsername/wordle-solver-fullstack.git)
cd wordle-solver-fullstack

```

### 2. Backend Setup

Open a terminal and run the following commands from the project root:

```
# Move into the backend directory
cd backend

# Create and activate a Python virtual environment
# On Windows
python -m venv .venv
.\.venv\Scripts\activate

# On macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend server
uvicorn app:app --reload

```

The API server will now be running on `http://localhost:8000`.

### 3. Frontend Setup

Open a **second terminal** and run the following commands from the project root:

```
# Move into the frontend directory
cd frontend

# Install dependencies
npm install

# Run the frontend development server
npm run dev

```

The React application will now be running on `http://localhost:5173`. Open this URL in your browser to use the app.