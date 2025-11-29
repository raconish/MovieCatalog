# ----------------------------- IMPORTS -----------------------------
import hashlib
from typing import Optional, List

from fastapi import FastAPI, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.sql import func

from database import SessionLocal
import crud
from models import Director, Genre, Movie, Review, User

# ----------------------------- APP INITIALIZATION -----------------------------
app = FastAPI()

# ----------------------------- DATABASE DEPENDENCY -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------------- AUTH HELPERS -----------------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash

def get_current_user(request: Request, db=Depends(get_db)) -> Optional[User]:
    username = request.cookies.get("username")
    if not username:
        return None
    return db.query(User).filter(User.username == username).first()

# ----------------------------- TEMPLATE & STATIC SETUP -----------------------------
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ----------------------------- Pydantic SCHEMAS (API) -----------------------------
class MovieCreate(BaseModel):
    title: str
    year: int
    description: Optional[str] = None
    director_id: int
    genre_ids: List[int]
    image_url: Optional[str] = None

class MovieOut(BaseModel):
    id: int
    title: str
    year: int
    description: Optional[str]
    director: Optional[str]
    genres: List[str]
    image_url: Optional[str]

    class Config:
        orm_mode = True

# ----------------------------- API HELPERS -----------------------------
def movie_to_out(movie: Movie) -> MovieOut:
    return MovieOut(
        id=movie.id,
        title=movie.title,
        year=movie.year,
        description=movie.description,
        director=movie.director.name if movie.director else None,
        genres=[g.name for g in movie.genres],
        image_url=movie.image_url,
    )

# ----------------------------- HTML ROUTES -----------------------------
@app.get("/", response_class=HTMLResponse)
def home(
    request: Request,
    db=Depends(get_db),
    q: str = "",
    genre: str = "",
    sort: str = "title",
    user: Optional[User] = Depends(get_current_user),
):
    query = db.query(Movie).join(Movie.director).outerjoin(Movie.genres)

    if q:
        query = query.filter(
            (Movie.title.ilike(f"%{q}%"))
            | (Movie.description.ilike(f"%{q}%"))
            | (Director.name.ilike(f"%{q}%"))
            | (Genre.name.ilike(f"%{q}%"))
        )

    if genre:
        query = query.filter(Genre.name.ilike(f"%{genre}%"))

    if sort == "year":
        query = query.order_by(Movie.year)
    elif sort == "rating":
        query = (
            query.outerjoin(Movie.reviews)
            .group_by(Movie.id)
            .order_by(func.avg(Review.rating).desc())
        )
    else:
        query = query.order_by(Movie.title)

    movies = query.all()

    for movie in movies:
        if movie.reviews:
            movie.avg_rating = sum(r.rating for r in movie.reviews) / len(movie.reviews)
        else:
            movie.avg_rating = None

    genres = db.query(Genre).all()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "movies": movies,
            "q": q,
            "genre": genre,
            "sort": sort,
            "genres": genres,
            "user": user,
        },
    )

# ---------- Login / Logout ----------
@app.get("/login", response_class=HTMLResponse)
def show_login(
    request: Request,
    next: str = "/",
    user: Optional[User] = Depends(get_current_user),
):
    if user:
        return RedirectResponse(url=next, status_code=303)
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": None, "next": next},
    )

@app.post("/login", response_class=HTMLResponse)
def handle_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    next: str = Form("/"),
    db=Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid username or password.",
                "next": next,
            },
            status_code=400,
        )

    response = RedirectResponse(url=next or "/", status_code=303)
    response.set_cookie("username", user.username, httponly=True)
    return response

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("username")
    return response

# ---------- Add movie (HTML) ----------
@app.get("/add", response_class=HTMLResponse)
def show_add_movie_form(
    request: Request,
    db=Depends(get_db),
    user: Optional[User] = Depends(get_current_user),
):
    if not user:
        return RedirectResponse(url="/login?next=/add", status_code=303)

    directors = db.query(Director).all()
    genres = db.query(Genre).all()
    return templates.TemplateResponse(
        "add_movie.html",
        {
            "request": request,
            "directors": directors,
            "genres": genres,
            "user": user,
        },
    )

@app.post("/add", response_class=HTMLResponse)
def handle_add_movie(
    request: Request,
    title: str = Form(...),
    year: int = Form(...),
    description: str = Form(""),
    director_name: str = Form(...),
    genre_name: str = Form(""),
    image_url: str = Form(""),
    db=Depends(get_db),
    user: Optional[User] = Depends(get_current_user),
):
    if not user:
        return RedirectResponse(url="/login?next=/add", status_code=303)

    genre_names = [g.strip() for g in genre_name.split(",") if g.strip()]
    crud.create_movie_with_names(
        db=db,
        title=title,
        year=year,
        description=description or None,
        director_name=director_name,
        genre_names=genre_names,
        image_url=image_url or None,
    )

    return RedirectResponse(url="/", status_code=303)

# ---------- Edit movie (HTML) ----------
@app.get("/edit/{movie_id}", response_class=HTMLResponse)
def show_edit_movie_form(
    request: Request,
    movie_id: int,
    db=Depends(get_db),
    user: Optional[User] = Depends(get_current_user),
):
    if not user:
        return RedirectResponse(url=f"/login?next=/edit/{movie_id}", status_code=303)

    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        movies = crud.get_movies(db)
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "movies": movies,
                "message": "Movie not found",
                "user": user,
            },
        )

    directors = db.query(Director).all()
    genres = db.query(Genre).all()
    return templates.TemplateResponse(
        "edit_movie.html",
        {
            "request": request,
            "movie": movie,
            "directors": directors,
            "genres": genres,
            "user": user,
        },
    )

@app.post("/edit/{movie_id}", response_class=HTMLResponse)
def handle_edit_movie(
    request: Request,
    movie_id: int,
    title: str = Form(...),
    year: int = Form(...),
    description: str = Form(""),
    director_name: str = Form(...),
    genre_name: str = Form(""),
    image_url: str = Form(""),
    db=Depends(get_db),
    user: Optional[User] = Depends(get_current_user),
):
    if not user:
        return RedirectResponse(url=f"/login?next=/edit/{movie_id}", status_code=303)

    genre_names = [g.strip() for g in genre_name.split(",") if g.strip()]
    updated = crud.update_movie_with_names(
        db=db,
        movie_id=movie_id,
        title=title,
        year=year,
        description=description or None,
        director_name=director_name,
        genre_names=genre_names,
        image_url=image_url or None,
    )
    if not updated:
        return RedirectResponse(url="/", status_code=303)

    return RedirectResponse(url="/", status_code=303)

# ---------- Delete movie (HTML) ----------
@app.get("/delete/{movie_id}", response_class=HTMLResponse)
def show_delete_confirmation(
    request: Request,
    movie_id: int,
    db=Depends(get_db),
    user: Optional[User] = Depends(get_current_user),
):
    if not user:
        return RedirectResponse(url=f"/login?next=/delete/{movie_id}", status_code=303)

    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        movies = crud.get_movies(db)
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "movies": movies,
                "message": "Movie not found",
                "user": user,
            },
        )
    return templates.TemplateResponse(
        "delete_movie.html",
        {"request": request, "movie": movie, "user": user},
    )

@app.post("/delete/{movie_id}", response_class=HTMLResponse)
def handle_delete_movie(
    request: Request,
    movie_id: int,
    db=Depends(get_db),
    user: Optional[User] = Depends(get_current_user),
):
    if not user:
        return RedirectResponse(url=f"/login?next=/delete/{movie_id}", status_code=303)

    success = crud.delete_movie(db, movie_id)
    movies = crud.get_movies(db)
    message = (
        f"Movie with ID {movie_id} deleted successfully!"
        if success
        else "Movie not found."
    )
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "movies": movies,
            "message": message,
            "user": user,
        },
    )

# ---------- Reviews & modal (HTML) ----------
@app.post("/movies/{movie_id}/review")
def add_review(
    movie_id: int,
    rating: int = Form(...),
    comment: str = Form(...),
    db=Depends(get_db),
):
    review = Review(
        movie_id=movie_id,
        rating=rating,
        comment=comment,
        user_name="Anonymous",
    )
    db.add(review)
    db.commit()
    return {"success": True}

@app.get("/movies/{movie_id}", response_class=HTMLResponse)
def get_movie_html(
    request: Request,
    movie_id: int,
    db=Depends(get_db),
    html: int = 0,
    user: Optional[User] = Depends(get_current_user),
):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()

    if html:
        return templates.TemplateResponse(
            "movie_modal.html",
            {"request": request, "movie": movie, "user": user},
        )

    return movie

# ----------------------------- API ROUTES (RESTFUL) -----------------------------
@app.get("/api/movies", response_model=List[MovieOut])
def api_get_movies(db=Depends(get_db)):
    movies = crud.get_movies(db)
    return [movie_to_out(m) for m in movies]

@app.get("/api/movies/{movie_id}", response_model=MovieOut)
def api_get_movie(movie_id: int, db=Depends(get_db)):
    movie = crud.get_movie(db, movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    return movie_to_out(movie)

@app.post("/api/movies", response_model=MovieOut, status_code=status.HTTP_201_CREATED)
def api_create_movie(movie_in: MovieCreate, db=Depends(get_db)):
    try:
        movie = crud.create_movie(
            db=db,
            title=movie_in.title,
            year=movie_in.year,
            description=movie_in.description,
            director_id=movie_in.director_id,
            genre_ids=movie_in.genre_ids,
            image_url=movie_in.image_url,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return movie_to_out(movie)

@app.put("/api/movies/{movie_id}", response_model=MovieOut)
def api_update_movie(movie_id: int, movie_in: MovieCreate, db=Depends(get_db)):
    try:
        movie = crud.update_movie(
            db=db,
            movie_id=movie_id,
            title=movie_in.title,
            year=movie_in.year,
            description=movie_in.description,
            director_id=movie_in.director_id,
            genre_ids=movie_in.genre_ids,
            image_url=movie_in.image_url,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    return movie_to_out(movie)

@app.delete("/api/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_delete_movie(movie_id: int, db=Depends(get_db)):
    success = crud.delete_movie(db, movie_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    return
