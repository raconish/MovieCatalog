# ----------------------------- IMPORTS -----------------------------
from database import SessionLocal
from models import Director, Genre, Movie, Review, Show, User
import hashlib

# ----------------------------- PASSWORD HELPERS -----------------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ----------------------------- MAIN SEED FUNCTION -----------------------------
def main():
    db = SessionLocal()
    try:
        nolan = Director(name="Christopher Nolan", birth_date="1970-07-30")
        sci_fi = Genre(name="Sci-Fi")

        inception = Movie(
            title="Inception",
            year=2010,
            description="A thief who steals corporate secrets through dream-sharing.",
            director=nolan,
            genres=[sci_fi],
        )

        review = Review(
            user_name="Amanda",
            rating=5,
            comment="Mind-bending classic!",
            movie=inception,
        )

        dark = Show(
            title="Dark",
            year=2017,
            description="A family saga with a time-travel twist.",
            director=nolan,
            genres=[sci_fi],
        )

        admin = User(
            username="admin",
            password_hash=hash_password("admin123"),
        )

        db.add_all([nolan, sci_fi, inception, review, dark, admin])
        db.commit()

        movies = db.query(Movie).all()
        print("Movies:", [m.title for m in movies])

    except Exception as e:
        print("❌ Error:", e)
        db.rollback()
    finally:
        db.close()

# ----------------------------- EXECUTION ENTRY POINT -----------------------------
if __name__ == "__main__":
    main()
