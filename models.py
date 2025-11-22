# ----------------------------- IMPORTS -----------------------------
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

# ----------------------------- ASSOCIATION TABLES -----------------------------
movie_genre_association = Table(
    "movie_genre_association",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id")),
    Column("genre_id", Integer, ForeignKey("genres.id"))
)

#NTS: It’s a bridge table — also called an association or junction table.
#It’s used when you have a many-to-many relationship.
#E.g. 
#One movie can have many genres (e.g., Inception → Action, Sci-Fi).
#One genre can belong to many movies (e.g., Sci-Fi → Inception, Interstellar).
#Relational databases don’t support that directly, so you create a middle table that links them.
#Same for genre, since they both need multiple relations.

show_genre_association = Table(
    "show_genre_association",
    Base.metadata,
    Column("show_id", Integer, ForeignKey("shows.id")),
    Column("genre_id", Integer, ForeignKey("genres.id"))
)

# ----------------------------- DIRECTOR MODEL -----------------------------
class Director(Base):
    __tablename__ = "directors"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    birth_date = Column(String)

    movies = relationship("Movie", back_populates="director")
    shows = relationship("Show", back_populates="director")

# ----------------------------- GENRE MODEL -----------------------------
class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    movies = relationship("Movie", secondary=movie_genre_association, back_populates="genres")
    shows = relationship("Show", secondary=show_genre_association, back_populates="genres")  # ✅ added this

# ----------------------------- MOVIE MODEL -----------------------------
class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False, index=True)
    year = Column(Integer)
    description = Column(Text)
    image_url = Column(String)
    director_id = Column(Integer, ForeignKey("directors.id"))

    director = relationship("Director", back_populates="movies")
    genres = relationship("Genre", secondary=movie_genre_association, back_populates="movies")

    reviews = relationship("Review", back_populates="movie", cascade="all, delete-orphan")
    
#NTS: Without the secondary, SQLAlchemy assumes a one-to-many relationship (simple foreign key).

# ----------------------------- REVIEW MODEL -----------------------------
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    user_name = Column(String, nullable=False)
    rating = Column(Integer)
    comment = Column(Text)

    movie_id = Column(Integer, ForeignKey("movies.id"))
    movie = relationship("Movie", back_populates="reviews")

# ----------------------------- SHOW MODEL -----------------------------
class Show(Base):
    __tablename__ = "shows"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False, index=True)
    year = Column(Integer)
    description = Column(Text)

    director_id = Column(Integer, ForeignKey("directors.id"))
    director = relationship("Director", back_populates="shows")

    genres = relationship("Genre", secondary=show_genre_association, back_populates="shows")  # ✅ fixed this
