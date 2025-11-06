# seedtest.py
from database import SessionLocal
from models import Director, Genre, Movie, Review, Show

def main():
    db = SessionLocal()
    try:
        # 1️⃣ Create sample director and genre
        nolan = Director(name="Christopher Nolan", birth_date="1970-07-30")
        sci_fi = Genre(name="Sci-Fi")

        # 2️⃣ Create a movie linked to them
        inception = Movie(
            title="Inception",
            year=2010,
            description="A thief who steals corporate secrets through dream-sharing.",
            director=nolan,
            genre=sci_fi
        )

        # 3️⃣ Create a review for the movie
        review = Review(
            user_name="Amanda",
            rating=5,
            comment="Mind-bending classic!",
            movie=inception
        )

        # 4️⃣ Create a show linked to same director & genre
        dark = Show(
            title="Dark",
            year=2017,
            description="A family saga with a time-travel twist.",
            director=nolan,
            genre=sci_fi
        )

        # 5️⃣ Add everything to the database
        db.add_all([nolan, sci_fi, inception, review, dark])
        db.commit()

        # 6️⃣ Optional: print out data to confirm
        movies = db.query(Movie).all()
        print(f"Movies: {[m.title for m in movies]}")

        shows = db.query(Show).all()
        print(f"Shows: {[s.title for s in shows]}")

        revs = db.query(Review).all()
        print(f"Reviews: {[f'{r.user_name} -> {r.rating}' for r in revs]}")

    except Exception as e:
        print("❌ Error:", e)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
