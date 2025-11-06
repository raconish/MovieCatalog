# ----------------------------- IMPORTS -----------------------------
from database import Base, engine
from models import Director, Genre, Movie, Review, Show  # Import all models

# ----------------------------- MAIN FUNCTION -----------------------------
def main():
    print("Creating tables...")               # Notify user before table creation
    Base.metadata.create_all(bind=engine)     # Create all tables defined in models
    print("Done.")                            # Confirm completion

# ----------------------------- EXECUTION ENTRY POINT -----------------------------
if __name__ == "__main__":
    main()  # Run main() when executed directly
