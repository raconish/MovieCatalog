# ----------------------------- IMPORTS -----------------------------
from database import Base, engine
from models import Director, Genre, Movie, Review, Show, User

# ----------------------------- MAIN FUNCTION -----------------------------
def main():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Done.")

# ----------------------------- EXECUTION ENTRY POINT -----------------------------
if __name__ == "__main__":
    main()
