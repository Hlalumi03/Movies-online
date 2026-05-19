import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import engine, get_db, Base
from dotenv import load_dotenv

load_dotenv()

# create DB tables if not using alembic for dev
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Movies Online")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend
static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

@app.get('/api/movies', response_model=list[schemas.MovieOut])
def api_search_movies(q: str | None = None, category: str | None = None, year: int | None = None, min_rating: float | None = None, page: int = 1, per_page: int = 20, db: Session = Depends(get_db)):
    items, total = crud.search_movies(db, q=q, category=(category or '').strip(), year=year, min_rating=min_rating, page=page, per_page=per_page)
    return items

@app.get('/api/movies/{movie_id}', response_model=schemas.MovieOut)
def api_get_movie(movie_id:int, db: Session = Depends(get_db)):
    m = crud.get_movie(db, movie_id)
    if not m:
        raise HTTPException(status_code=404, detail='Movie not found')
    return m

@app.post('/api/reviews', response_model=schemas.ReviewOut)
def api_create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    r = crud.create_review(db, review)
    if not r:
        raise HTTPException(status_code=404, detail='Movie not found')
    return r

@app.post('/api/movies', response_model=schemas.MovieOut)
def api_create_movie(movie: schemas.MovieCreate, db: Session = Depends(get_db)):
    m = crud.create_movie(db, movie)
    return m
