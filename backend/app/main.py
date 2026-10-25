import os
from fastapi import FastAPI, Depends, HTTPException, Path, Query
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from . import crud, schemas
from .database import get_db
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Movies Online")


@app.get("/api/categories", response_model=list[schemas.CategoryOut])
def api_list_categories(db: Session = Depends(get_db)):
    return crud.list_categories(db)


@app.get("/api/movie-filters", response_model=schemas.MovieFilters)
def api_movie_filters(db: Session = Depends(get_db)):
    years = crud.list_movie_years(db)
    return {"years": [year for (year,) in years]}


@app.get("/api/recommendations", response_model=list[schemas.MovieOut])
def api_recommendations(db: Session = Depends(get_db)):
    return crud.list_recommendations(db)


@app.get("/api/movies", response_model=schemas.MoviePage)
def api_search_movies(
    q: str | None = None,
    category: str | None = None,
    year: int | None = Query(default=None, ge=1888, le=2100),
    min_rating: float | None = Query(default=None, ge=0, le=5),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = crud.search_movies(db, q=q, category=(category or '').strip(), year=year, min_rating=min_rating, page=page, per_page=per_page)
    return {"items": items, "total": total, "page": page, "per_page": per_page}


@app.get("/api/movies/{movie_id}", response_model=schemas.MovieDetailOut)
def api_get_movie(movie_id: int = Path(gt=0), db: Session = Depends(get_db)):
    m = crud.get_movie_detail(db, movie_id)
    if not m:
        raise HTTPException(status_code=404, detail="Movie not found")
    return m


@app.post("/api/reviews", response_model=schemas.ReviewOut)
def api_create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    r = crud.create_review(db, review)
    if not r:
        raise HTTPException(status_code=404, detail="Movie not found")
    return r


@app.post("/api/movies", response_model=schemas.MovieOut)
def api_create_movie(movie: schemas.MovieCreate, db: Session = Depends(get_db)):
    return crud.create_movie(db, movie)


static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
