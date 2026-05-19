from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas
from typing import List, Optional


def get_or_create_category(db: Session, name: str):
    name = name.strip()
    cat = db.query(models.Category).filter(func.lower(models.Category.name) == name.lower()).first()
    if cat:
        return cat
    cat = models.Category(name=name)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


def create_movie(db: Session, movie: schemas.MovieCreate):
    m = models.Movie(title=movie.title, year=movie.year, description=movie.description)
    for cname in movie.categories:
        cat = get_or_create_category(db, cname)
        m.categories.append(cat)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


def get_movie(db: Session, movie_id: int):
    return db.query(models.Movie).filter(models.Movie.id==movie_id).first()


def search_movies(db: Session, q: Optional[str]=None, category: Optional[str]=None, year: Optional[int]=None, min_rating: Optional[float]=None, page:int=1, per_page:int=20):
    query = db.query(models.Movie)
    if q:
        query = query.filter(models.Movie.title.ilike(f"%{q}%"))
    if category:
        query = query.join(models.Movie.categories).filter(models.Category.name.ilike(category))
    if year:
        query = query.filter(models.Movie.year==year)
    if min_rating:
        query = query.filter(models.Movie.avg_rating >= min_rating)
    total = query.count()
    items = query.order_by(models.Movie.avg_rating.desc()).offset((page-1)*per_page).limit(per_page).all()
    return items, total


def create_review(db: Session, review_in: schemas.ReviewCreate):
    movie = get_movie(db, review_in.movie_id)
    if not movie:
        return None
    r = models.Review(movie_id=review_in.movie_id, rating=review_in.rating, text=review_in.text)
    db.add(r)
    db.commit()
    # update avg rating
    avg = db.query(func.avg(models.Review.rating)).filter(models.Review.movie_id==movie.id).scalar() or 0
    movie.avg_rating = float(round(avg,2))
    db.add(movie)
    db.commit()
    db.refresh(r)
    return r
