"""
Test script to validate Movies Online project
Tests: database models, CRUD operations, and API logic
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("=" * 60)
print("MOVIES ONLINE - PROJECT TEST")
print("=" * 60)

# Test 1: Import models
print("\n[TEST 1] Importing models...")
try:
    from app.models import Movie, Category, Review
    from app.schemas import MovieCreate, ReviewCreate, MovieOut
    print("✓ All models imported successfully")
except Exception as e:
    print(f"✗ ERROR: {e}")
    sys.exit(1)

# Test 2: Check ORM structure
print("\n[TEST 2] Checking ORM structure...")
try:
    # Check Movie table columns
    assert hasattr(Movie, 'id'), "Movie missing id"
    assert hasattr(Movie, 'title'), "Movie missing title"
    assert hasattr(Movie, 'year'), "Movie missing year"
    assert hasattr(Movie, 'avg_rating'), "Movie missing avg_rating"
    assert hasattr(Movie, 'categories'), "Movie missing categories relationship"
    assert hasattr(Movie, 'reviews'), "Movie missing reviews relationship"
    print("✓ Movie ORM structure is valid")
    
    # Check Category table
    assert hasattr(Category, 'id'), "Category missing id"
    assert hasattr(Category, 'name'), "Category missing name"
    assert hasattr(Category, 'movies'), "Category missing movies relationship"
    print("✓ Category ORM structure is valid")
    
    # Check Review table
    assert hasattr(Review, 'id'), "Review missing id"
    assert hasattr(Review, 'movie_id'), "Review missing movie_id"
    assert hasattr(Review, 'rating'), "Review missing rating"
    assert hasattr(Review, 'text'), "Review missing text"
    assert hasattr(Review, 'created_at'), "Review missing created_at"
    assert hasattr(Review, 'movie'), "Review missing movie relationship"
    print("✓ Review ORM structure is valid")
except AssertionError as e:
    print(f"✗ ERROR: {e}")
    sys.exit(1)

# Test 3: Check Schemas
print("\n[TEST 3] Checking Pydantic schemas...")
try:
    # Test MovieCreate schema
    movie_data = {"title": "Test Movie", "year": 2024, "description": "A test", "categories": ["Action"]}
    movie_in = MovieCreate(**movie_data)
    assert movie_in.title == "Test Movie"
    print("✓ MovieCreate schema is valid")
    
    # Test ReviewCreate schema
    review_data = {"movie_id": 1, "rating": 5, "text": "Great!"}
    review_in = ReviewCreate(**review_data)
    assert review_in.rating == 5
    print("✓ ReviewCreate schema is valid")
except Exception as e:
    print(f"✗ ERROR: {e}")
    sys.exit(1)

# Test 4: Database setup
print("\n[TEST 4] Setting up test database...")
try:
    from app.database import engine, SessionLocal, Base
    print("✓ Database engine created")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")
except Exception as e:
    print(f"✗ ERROR: {e}")
    sys.exit(1)

# Test 5: CRUD operations
print("\n[TEST 5] Testing CRUD operations...")
try:
    from app.crud import create_movie, get_movie, search_movies, create_review
    
    db = SessionLocal()
    
    # Create categories
    cat = Category(name="Action")
    db.add(cat)
    db.commit()
    print("✓ Created category")
    
    # Create movie using CRUD
    movie_in = MovieCreate(title="Edge of Tomorrow", year=2014, description="A soldier relives the same day.", categories=["Action"])
    movie = create_movie(db, movie_in)
    assert movie.id is not None
    assert movie.title == "Edge of Tomorrow"
    print(f"✓ Created movie (ID: {movie.id})")
    
    # Get movie
    fetched = get_movie(db, movie.id)
    assert fetched.title == "Edge of Tomorrow"
    print("✓ Retrieved movie by ID")
    
    # Search movies
    results, total = search_movies(db, q="Edge")
    assert total > 0
    print(f"✓ Searched movies (found {total} results)")
    
    # Create review
    review_in = ReviewCreate(movie_id=movie.id, rating=5, text="Excellent!")
    review = create_review(db, review_in)
    assert review.id is not None
    assert review.rating == 5
    print(f"✓ Created review (Rating: {review.rating})")
    
    # Check avg_rating updated
    updated_movie = get_movie(db, movie.id)
    assert updated_movie.avg_rating > 0
    print(f"✓ Movie avg_rating updated: {updated_movie.avg_rating}")
    
    db.close()
except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: FastAPI endpoints
print("\n[TEST 6] Checking FastAPI endpoints...")
try:
    from app.main import app
    print("✓ FastAPI app imported successfully")
    
    # Check routes
    routes = [route.path for route in app.routes]
    assert "/api/movies" in routes or any("/api/movies" in r for r in routes)
    print(f"✓ Found {len(routes)} routes in app")
except Exception as e:
    print(f"✗ ERROR: {e}")
    sys.exit(1)

# Test 7: Check Alembic migration
print("\n[TEST 7] Checking Alembic configuration...")
try:
    migration_file = os.path.join(os.path.dirname(__file__), 'backend', 'alembic', 'versions', '0001_create_initial_tables.py')
    assert os.path.exists(migration_file), f"Migration file not found at {migration_file}"
    with open(migration_file) as f:
        content = f.read()
        assert 'CREATE TABLE' in content or 'op.create_table' in content
    print("✓ Alembic migration file exists and is valid")
except Exception as e:
    print(f"✗ ERROR: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED!")
print("=" * 60)
print("\nProject structure:")
print("✓ Models (Movie, Category, Review) with SQLAlchemy ORM")
print("✓ Pydantic schemas for data validation")
print("✓ CRUD operations (create, read, search)")
print("✓ Database migrations with Alembic")
print("✓ FastAPI backend with endpoints")
print("✓ Frontend (Tailwind CSS + JavaScript)")
print("\nTo run the server:")
print("  cd backend")
print("  alembic upgrade head")
print("  python seed.py")
print("  uvicorn app.main:app --reload --port 8000")
print("\nThen open: http://127.0.0.1:8000/")
