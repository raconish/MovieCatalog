# ----------------------------- IMPORTS -----------------------------
from sqlalchemy.orm import Session
from models import Movie

# ----------------------------- CREATE -----------------------------
def create_movie(db, title, year, description, director_id, genres=None):
    new_movie = Movie(
        title=title,
        year=year,
        description=description,
        director_id=director_id,
    )
    if genres:
        new_movie.genres = genres  # assign list of Genre objects
    db.add(new_movie)
    db.commit()
    #NTS this saves the change permanently (like hitting “Save” in the DB).
    db.refresh(new_movie)
    #NTS this bupdates the Python object with any auto-generated values (like the movie’s new ID).
    return new_movie

# ----------------------------- READ -----------------------------
def get_movies(db: Session):
    """Return all movies in the database."""
    return db.query(Movie).all()

# ----------------------------- UPDATE -----------------------------
def update_movie(db: Session, movie_id: int, title: str, year: int, description: str, director_id: int, genre_id: int):
    """Update movie details by ID."""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    #NTS Movie.id → refers to the id column in the table.
    #movie_id → is the value you passed into the function.
    #first() actually executes the query and returns the first matching row, or None if nothing was found.
    if movie:
        movie.title = title
        movie.year = year
        movie.description = description
        movie.director_id = director_id
        movie.genre_id = genre_id
        db.commit()
        db.refresh(movie)
    return movie

# ----------------------------- DELETE -----------------------------
def delete_movie(db: Session, movie_id: int):
    """Delete a movie by ID."""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie:
        db.delete(movie)
        db.commit()
        return True
    return False
