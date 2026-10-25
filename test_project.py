"""HTTP-level tests for the Movies Online application."""

import os
import sys
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.database import Base, get_db
from app.main import app


test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


class MoviesApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        cls.client.close()
        app.dependency_overrides.clear()
        test_engine.dispose()

    def setUp(self):
        Base.metadata.drop_all(bind=test_engine)
        Base.metadata.create_all(bind=test_engine)

    def create_movie(self, title="Arrival", categories=None):
        return self.client.post(
            "/api/movies",
            json={
                "title": title,
                "year": 2016,
                "description": "A linguist studies an alien language.",
                "categories": categories or ["Drama", "Sci-Fi"],
            },
        )

    def test_frontend_and_api_routes_are_served(self):
        page = self.client.get("/")
        self.assertEqual(page.status_code, 200)
        self.assertIn("Movies Online", page.text)
        self.assertLess(page.text.index('id="browse"'), page.text.index('id="recommendationSection"'))

        script = self.client.get("/app.js")
        self.assertEqual(script.status_code, 200)
        self.assertIn("loadRecommendations", script.text)
        self.assertIn("const pageSize = 10", script.text)

        movies = self.client.get("/api/movies")
        self.assertEqual(movies.status_code, 200)
        self.assertEqual(movies.json()["items"], [])

    def test_categories_and_paginated_search(self):
        self.create_movie("Arrival")
        self.create_movie("Another World", categories=["Drama"])

        categories = self.client.get("/api/categories")
        self.assertEqual([item["name"] for item in categories.json()], ["Drama", "Sci-Fi"])

        results = self.client.get("/api/movies", params={"category": "Drama", "page": 1, "per_page": 1})
        self.assertEqual(results.status_code, 200)
        self.assertEqual(results.json()["total"], 2)
        self.assertEqual(results.json()["page"], 1)
        self.assertEqual(results.json()["per_page"], 1)
        self.assertEqual(len(results.json()["items"]), 1)

        unrated = self.client.get("/api/movies", params={"min_rating": 0})
        self.assertEqual(unrated.status_code, 200)
        self.assertEqual(unrated.json()["total"], 2)

    def test_exact_title_search_returns_only_the_exact_movie(self):
        self.create_movie("The Matrix")
        exact = self.create_movie("Matrix")
        self.create_movie("Matrix Reloaded")

        response = self.client.get("/api/movies", params={"q": "Matrix"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(response.json()["items"][0]["id"], exact.json()["id"])

    def test_filter_options_and_recommendations(self):
        movie = self.create_movie("Arrival")
        self.create_movie("Another World")

        filters = self.client.get("/api/movie-filters")
        self.assertEqual(filters.status_code, 200)
        self.assertEqual(filters.json()["years"], [2016])

        recommendations = self.client.get("/api/recommendations")
        self.assertEqual(recommendations.status_code, 200)
        self.assertEqual(len(recommendations.json()), 2)
        recommended_ids = {item["id"] for item in recommendations.json()}
        self.assertIn(movie.json()["id"], recommended_ids)

    def test_movie_details_and_review_submission_update_average(self):
        created = self.create_movie()
        self.assertEqual(created.status_code, 200)
        movie_id = created.json()["id"]

        review = self.client.post(
            "/api/reviews",
            json={"movie_id": movie_id, "rating": 5, "text": "Excellent."},
        )
        self.assertEqual(review.status_code, 200)

        details = self.client.get(f"/api/movies/{movie_id}")
        self.assertEqual(details.status_code, 200)
        self.assertEqual(details.json()["avg_rating"], 5.0)
        self.assertEqual(details.json()["reviews"][0]["text"], "Excellent.")

    def test_invalid_review_rating_is_rejected(self):
        movie_id = self.create_movie().json()["id"]
        response = self.client.post(
            "/api/reviews",
            json={"movie_id": movie_id, "rating": 6, "text": "Too high."},
        )
        self.assertEqual(response.status_code, 422)

    def test_invalid_pagination_is_rejected(self):
        response = self.client.get("/api/movies", params={"page": 0})
        self.assertEqual(response.status_code, 422)

    def test_movie_creation_normalizes_categories_and_title(self):
        response = self.create_movie(
            title="  Arrival  ",
            categories=["Drama", " drama "],
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Arrival")
        self.assertEqual([item["name"] for item in response.json()["categories"]], ["Drama"])

    def test_missing_movie_returns_not_found(self):
        response = self.client.get("/api/movies/999")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
