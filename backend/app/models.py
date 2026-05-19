from sqlalchemy import Column, Integer, String, Text, Float, Table, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base
import datetime

movie_category = Table(
    'movie_category',
    Base.metadata,
    Column('movie_id', ForeignKey('movies.id'), primary_key=True),
    Column('category_id', ForeignKey('categories.id'), primary_key=True)
)

class Movie(Base):
    __tablename__ = 'movies'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    year = Column(Integer, index=True)
    description = Column(Text)
    avg_rating = Column(Float, default=0.0)
    categories = relationship('Category', secondary=movie_category, back_populates='movies')
    reviews = relationship('Review', back_populates='movie', cascade="all, delete-orphan")

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    movies = relationship('Movie', secondary=movie_category, back_populates='categories')

class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    text = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    movie = relationship('Movie', back_populates='reviews')
