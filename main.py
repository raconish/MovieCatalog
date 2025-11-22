# ----------------------------- IMPORTS -----------------------------
from fastapi import FastAPI, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from database import SessionLocal
import crud
from models import Director, Genre, Movie
from fastapi.responses import RedirectResponse

# ----------------------------- APP INITIALIZATION -----------------------------
app = FastAPI()  # Starts the FastAPI application

# ----------------------------- DATABASE DEPENDENCY -----------------------------
def get_db():
    """Dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
        #NTS keyword that temporarily hands over something (like a database connection)
        #NTS to the caller and then continues after that point once the work is done
    finally:
        db.close()

# ----------------------------- TEMPLATE & STATIC SETUP -----------------------------
templates = Jinja2Templates(directory="templates")             # Jinja2 templates folder
app.mount("/static", StaticFiles(directory="static"), name="static")  # Mount static files (CSS, JS, images)
#NTS app.mount is telling where to find the templates (shop display/directions to where to find them)
# ----------------------------- HOME PAGE -----------------------------
@app.get("/", response_class=HTMLResponse)
#NTS to show an HTML page
#by deafult, when using FastAPI, the page uses JSON to return formats, so we need to specify it will be 
#HLTML instead
def home(
    request: Request, #NTS incoming request itself (letter that we receive with the information)
    db = Depends(get_db),
    q: str = "",        # search text
    genre: str = "",    # filter by genre name
    sort: str = "title" # sort by title or year
):
    """Render homepage with search, filter, and sort."""

    # Start a base query
    query = db.query(Movie).join(Movie.director).outerjoin(Movie.genres)
    #NTS building a db query, using SQLAlchemy inside Python

    # 🔍 Search by title, description, director, or genre
    if q:
        query = query.filter(
            (Movie.title.ilike(f"%{q}%")) |
            (Movie.description.ilike(f"%{q}%")) |
            (Director.name.ilike(f"%{q}%")) |
            (Genre.name.ilike(f"%{q}%"))

            #NTS Look for this text anywhere in the title, description, director, or genre
            #NTS The ilike function just makes the search case-insensitive, so it doesn’t 
            #NTS matter if the user types uppercase or lowercase letters
            #NTS The f there is just for something called an f-string in Python. It’s a way to 
            #format strings, and it lets you put variables inside curly braces right inside the string. 
            #So when you see f"%{q}%", it’s just putting the value of the variable q into the string
        )

    # 🎬 Filter by genre
    if genre:
        query = query.filter(Genre.name.ilike(f"%{genre}%"))

    # ↕️ Sort results
    if sort == "year":
        query = query.order_by(Movie.year)
    else:
        query = query.order_by(Movie.title)

    # Run the query
    movies = query.all()

    # Load all genres for the filter dropdown
    genres = db.query(Genre).all()

    # Return the rendered page
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "movies": movies,
            "q": q,
            "genre": genre,
            "sort": sort,
            "genres": genres
        }
    )


# ----------------------------- GET: ALL MOVIES (API ENDPOINT) -----------------------------
@app.get("/movies")
def list_movies(db = Depends(get_db)):
    """Return all movies as JSON for API testing (e.g., Swagger UI)."""
    movies = crud.get_movies(db)
    return [
        {
            "id": m.id,
            "title": m.title,
            "year": m.year,
            "description": m.description,
            "director_id": m.director_id,
            "genre_id": m.genre_id
        }
        for m in movies
    ]

# ----------------------------- CREATE: ADD MOVIE (API) -----------------------------
@app.post("/movies")
def add_movie(
    title: str = Form(...),
    year: int = Form(...),
    description: str = Form(...),
    director_id: int = Form(...),
    genre_id: int = Form(...),
    db = Depends(get_db)
):
    """Add a new movie through API."""
    movie = crud.create_movie(db, title, year, description, director_id, genre_id)
    return {
        "message": "Movie added successfully!",
        "movie": {
            "id": movie.id,
            "title": movie.title,
            "year": movie.year,
            "description": movie.description,
            "director_id": movie.director_id,
            "genre_id": movie.genre_id
        }
    }

# ----------------------------- UPDATE: EDIT MOVIE (API) -----------------------------
@app.put("/movies/{movie_id}")
def edit_movie(
    movie_id: int,
    title: str = Form(...),
    year: int = Form(...),
    description: str = Form(...),
    director_id: int = Form(...),
    genre_id: int = Form(...),
    db = Depends(get_db)
):
    """Update an existing movie via API."""
    movie = crud.update_movie(db, movie_id, title, year, description, director_id, genre_id)
    if not movie:
        return {"error": "Movie not found"}
    return {
        "message": "Movie updated successfully!",
        "movie": {
            "id": movie.id,
            "title": movie.title,
            "year": movie.year,
            "description": movie.description,
            "director_id": movie.director_id,
            "genre_id": movie.genre_id
        }
    }

# ----------------------------- DELETE: REMOVE MOVIE (API) -----------------------------
@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int, db = Depends(get_db)):
    """Delete a movie via API."""
    success = crud.delete_movie(db, movie_id)
    if not success:
        return {"error": "Movie not found"}
    return {"message": f"Movie with ID {movie_id} deleted successfully!"}

# ----------------------------- ADD MOVIE PAGE -----------------------------
@app.get("/add", response_class=HTMLResponse)
def show_add_movie_form(request: Request, db = Depends(get_db)):
    directors = db.query(Director).all()
    genres = db.query(Genre).all()
    return templates.TemplateResponse(
        "add_movie.html",
        {"request": request, "directors": directors, "genres": genres}
    )

# ----------------------------- HANDLE ADD MOVIE FORM -----------------------------
@app.post("/add", response_class=HTMLResponse)
def handle_add_movie(
    request: Request,
    title: str = Form(...),
    year: int = Form(...),
    description: str = Form(...),
    director_name: str = Form(...),
    genre_name: str = Form(...),   # This can now be multiple, comma-separated
    image_url: str = Form(""),
    db = Depends(get_db)
):
    from models import Director, Genre

    # 🎬 Find or create director
    director = db.query(Director).filter(Director.name.ilike(director_name)).first()
    if not director:
        director = Director(name=director_name)
        db.add(director)
        db.commit()
        db.refresh(director)

    # 🎭 Handle multiple genres (split by commas)
    genre_names = [g.strip() for g in genre_name.split(",") if g.strip()]
    genres = []
    for name in genre_names:
        genre = db.query(Genre).filter(Genre.name.ilike(name)).first()
        if not genre:
            genre = Genre(name=name)
            db.add(genre)
            db.commit()
            db.refresh(genre)
        genres.append(genre)

    # 🎞️ Create the movie with multiple genres
    movie = crud.create_movie(db, title, year, description, director.id, genres)
    movie.image_url = image_url
    db.commit()
    db.refresh(movie)

    # ✅ Redirect to home page after adding (prevents duplicates on refresh)
    response = RedirectResponse(url="/", status_code=303)
    return response


# ----------------------------- EDIT MOVIE PAGE -----------------------------
@app.get("/edit/{movie_id}", response_class=HTMLResponse)
def show_edit_movie_form(request: Request, movie_id: int, db = Depends(get_db)):
    """Render the Edit Movie form page with director/genre dropdowns."""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "movies": crud.get_movies(db), "message": "Movie not found"}
        )
    directors = db.query(Director).all()
    genres = db.query(Genre).all()
    return templates.TemplateResponse(
        "edit_movie.html",
        {"request": request, "movie": movie, "directors": directors, "genres": genres}
    )

# ----------------------------- HANDLE EDIT MOVIE FORM -----------------------------
@app.post("/edit/{movie_id}", response_class=HTMLResponse)
def handle_edit_movie(
    request: Request,
    movie_id: int,
    title: str = Form(...),
    year: int = Form(...),
    description: str = Form(...),
    director_name: str = Form(...),
    genre_name: str = Form(...),
    image_url: str = Form(""),
    db = Depends(get_db)
):
    from models import Director, Genre

    # Find or create director
    director = db.query(Director).filter(Director.name.ilike(director_name)).first()
    if not director:
        director = Director(name=director_name)
        db.add(director)
        db.commit()
        db.refresh(director)

    # Find or create genre
    genre = db.query(Genre).filter(Genre.name.ilike(genre_name)).first()
    if not genre:
        genre = Genre(name=genre_name)
        db.add(genre)
        db.commit()
        db.refresh(genre)

    # Update movie and poster
    movie = crud.update_movie(db, movie_id, title, year, description, director.id, genre.id)
    movie.image_url = image_url  # ✅ this is what saves the new poster link
    db.commit()
    db.refresh(movie)

    response = RedirectResponse(url="/", status_code=303)
    return response

# ----------------------------- DELETE CONFIRMATION PAGE -----------------------------
@app.get("/delete/{movie_id}", response_class=HTMLResponse)
def show_delete_confirmation(request: Request, movie_id: int, db = Depends(get_db)):
    """Render the Delete Movie confirmation page."""
    movie = db.query(crud.Movie).filter(crud.Movie.id == movie_id).first()
    if not movie:
        movies = crud.get_movies(db)
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "movies": movies, "message": "Movie not found"}
        )
    return templates.TemplateResponse("delete_movie.html", {"request": request, "movie": movie})

# ----------------------------- HANDLE DELETE MOVIE FORM -----------------------------
@app.post("/delete/{movie_id}", response_class=HTMLResponse)
def handle_delete_movie(request: Request, movie_id: int, db = Depends(get_db)):
    """Process Delete Movie form and reload main catalog."""
    success = crud.delete_movie(db, movie_id)
    movies = crud.get_movies(db)
    message = f"Movie with ID {movie_id} deleted successfully!" if success else "Movie not found."
    return templates.TemplateResponse("index.html", {"request": request, "movies": movies, "message": message})
