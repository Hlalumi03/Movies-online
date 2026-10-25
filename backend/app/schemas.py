from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional
from datetime import datetime


class OrmSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CategoryOut(OrmSchema):
    id: int
    name: str


class ReviewCreate(BaseModel):
    movie_id: int = Field(gt=0)
    rating: int = Field(ge=1, le=5)
    text: Optional[str] = Field(default=None, max_length=2000)

    @field_validator("text")
    @classmethod
    def strip_text(cls, value):
        return value.strip() or None if value is not None else None


class ReviewOut(OrmSchema):
    id: int
    movie_id: int
    rating: int
    text: Optional[str]
    created_at: datetime


class MovieOut(OrmSchema):
    id: int
    title: str
    year: Optional[int]
    description: Optional[str]
    avg_rating: float
    categories: list[CategoryOut] = Field(default_factory=list)


class MovieDetailOut(MovieOut):
    reviews: list[ReviewOut] = Field(default_factory=list)


class MoviePage(BaseModel):
    items: list[MovieOut]
    total: int
    page: int
    per_page: int


class MovieFilters(BaseModel):
    years: list[int]


class MovieCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    year: Optional[int] = Field(default=None, ge=1888, le=2100)
    description: Optional[str] = Field(default=None, max_length=10000)
    categories: list[str] = Field(default_factory=list, max_length=20)

    @field_validator("title")
    @classmethod
    def strip_title(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Title must not be blank")
        return value

    @field_validator("categories")
    @classmethod
    def normalize_categories(cls, categories):
        normalized = []
        seen = set()
        for category in categories:
            category = category.strip()
            if not category:
                raise ValueError("Category names must not be blank")
            if len(category) > 100:
                raise ValueError("Category names must be at most 100 characters")
            key = category.casefold()
            if key not in seen:
                normalized.append(category)
                seen.add(key)
        return normalized
