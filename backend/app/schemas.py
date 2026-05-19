from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CategoryOut(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True

class ReviewCreate(BaseModel):
    movie_id: int
    rating: int
    text: Optional[str] = None

class ReviewOut(BaseModel):
    id: int
    movie_id: int
    rating: int
    text: Optional[str]
    created_at: datetime
    class Config:
        orm_mode = True

class MovieOut(BaseModel):
    id: int
    title: str
    year: Optional[int]
    description: Optional[str]
    avg_rating: float
    categories: List[CategoryOut] = []
    class Config:
        orm_mode = True

class MovieCreate(BaseModel):
    title: str
    year: Optional[int]
    description: Optional[str]
    categories: List[str] = []
