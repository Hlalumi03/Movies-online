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

API endpoints:
- `GET /api/movies?q=&category=&year=&min_rating=` — search movies
- `GET /api/movies/{id}` — movie detail
- `POST /api/movies` — create movie
- `POST /api/reviews` — create review

If you want help running locally, deploying, or adding features (auth, video streaming, user accounts), tell me which part to implement next.
