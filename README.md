# Movies Online

A small fullstack example: FastAPI backend, SQLite database with Alembic migrations, and a modern static frontend served from the backend.

Quick start (Windows):

1. Create and activate a virtualenv, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

2. Create the database and run migrations (from `backend`):

```powershell
cd backend
alembic upgrade head
python seed.py
```

3. Start the app:

```powershell
uvicorn app.main:app --reload --port 8000
```

Open http://127.0.0.1:8000/ to view the frontend.

Features:
- Responsive movie search with popular category choices and release years found in the catalog.
- See top recommendations as soon as the page opens, before searching.
- Search by title, category, year, and rating; exact title matches are shown on their own, with up to 10 results per page.
- See recommendations below the search results; the movie already shown in the results is not repeated in recommendations.
- Open a movie to see its details and reviews, then submit a 1–5-star review.
- Movie scores update when reviews are submitted.

API endpoints:
- `GET /api/categories` — list available categories
- `GET /api/movie-filters` — list release years in the catalog
- `GET /api/recommendations` — list up to six recommended movies
- `GET /api/movies?q=&category=&year=&min_rating=&page=&per_page=` — search movies; returns `items`, `total`, `page`, and `per_page`. Page size is limited to 100.
- `GET /api/movies/{id}` — movie details including reviews
- `POST /api/movies` — create a movie
- `POST /api/reviews` — create a review (rating must be 1–5)

Run the project checks from the repository root:

```powershell
python test_project.py
```

If you want help running locally, deploying, or adding features (auth, video streaming, user accounts), tell me which part to implement next.
