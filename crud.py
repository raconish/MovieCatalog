# ----------------------------- IMPORTS -----------------------------
from typing import List, Optional
from sqlalchemy.orm import Session
from models import Movie, Director, Genre

# ----------------------------- DIRECTOR HELPERS -----------------------------
def get_director_by_id(db: Session, director_id: int) -> Optional[Director]:
    return db.query(Director).filter(Director.id == director_id).first()

def get_director_by_name(db: Session, name: str) -> Optional[Director]:
    return db.query(Director).filter(Director.name.ilike(name)).first()

def get_or_create_director_by_name(db: Session, name: str) -> Director:
    clean_name = name.strip()
    director = get_director_by_name(db, clean_name)
    if director:
        return director
    director = Director(name=clean_name)
    db.add(director)
    db.commit()
    db.refresh(director)
    return director

# ----------------------------- GENRE HELPERS -----------------------------
def get_genres_by_ids(db: Session, genre_ids: List[int]) -> List[Genre]:
    if not genre_ids:
        return []
    return db.query(Genre).filter(Genre.id.in_(genre_ids)).all()

def get_or_create_genres_by_names(db: Session, names: List[str]) -> List[Genre]:
    genres: List[Genre] = []
    for name in names:
        clean = name.strip()
        if not clean:
            continue
        genre = db.query(Genre).filter(Genre.name.ilike(clean)).first()
        if not genre:
            genre = Genre(name=clean)
            db.add(genre)
            db.commit()
            db.refresh(genre)
        genres.append(genre)
    return genres

# ----------------------------- MOVIE CRUD (ID-BASED, USED BY API) -----------------------------
def get_movies(db: Session) -> List[Movie]:
    return db.query(Movie).all()

def get_movie(db: Session, movie_id: int) -> Optional[Movie]:
    return db.query(Movie).filter(Movie.id == movie_id).first()

def create_movie(
    db: Session,
    title: str,
    year: int,
    description: Optional[str],
    director_id: int,
    genre_ids: List[int],
    image_url: Optional[str] = None,
) -> Movie:
    director = get_director_by_id(db, director_id)
    if not director:
        raise ValueError("Director not found")

    genres = get_genres_by_ids(db, genre_ids)

    movie = Movie(
        title=title,
        year=year,
        description=description,
        director=director,
        image_url=image_url,
    )
    movie.genres = genres

    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie

def update_movie(
    db: Session,
    movie_id: int,
    title: str,
    year: int,
    description: Optional[str],
    director_id: int,
    genre_ids: List[int],
    image_url: Optional[str] = None,
) -> Optional[Movie]:
    movie = get_movie(db, movie_id)
    if not movie:
        return None

    director = get_director_by_id(db, director_id)
    if not director:
        raise ValueError("Director not found")

    genres = get_genres_by_ids(db, genre_ids)

    movie.title = title
    movie.year = year
    movie.description = description
    movie.director = director
    movie.image_url = image_url
    movie.genres = genres

    db.commit()
    db.refresh(movie)
    return movie

def delete_movie(db: Session, movie_id: int) -> bool:
    movie = get_movie(db, movie_id)
    if not movie:
        return False
    db.delete(movie)
    db.commit()
    return True

# ----------------------------- MOVIE HELPERS (NAME-BASED, USED BY HTML FORMS) -----------------------------
def create_movie_with_names(
    db: Session,
    title: str,
    year: int,
    description: Optional[str],
    director_name: str,
    genre_names: List[str],
    image_url: Optional[str] = None,
) -> Movie:
    director = get_or_create_director_by_name(db, director_name)
    genres = get_or_create_genres_by_names(db, genre_names)
    return create_movie(
        db=db,
        title=title,
        year=year,
        description=description,
        director_id=director.id,
        genre_ids=[g.id for g in genres],
        image_url=image_url,
    )

def update_movie_with_names(
    db: Session,
    movie_id: int,
    title: str,
    year: int,
    description: Optional[str],
    director_name: str,
    genre_names: List[str],
    image_url: Optional[str] = None,
) -> Optional[Movie]:
    director = get_or_create_director_by_name(db, director_name)
    genres = get_or_create_genres_by_names(db, genre_names)
    return update_movie(
        db=db,
        movie_id=movie_id,
        title=title,
        year=year,
        description=description,
        director_id=director.id,
        genre_ids=[g.id for g in genres],
        image_url=image_url,
    )
