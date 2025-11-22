# ----------------------------- IMPORTS -----------------------------
from database import Base, engine
from models import Director, Genre, Movie, Review, Show  # Import all models

#NTS Its only job is to look at all the models you defined (like Movie, Director, etc.) and tell the database:
#“Hey, please create these tables if they don’t exist yet.”
#So it’s not for running your app — just a one-time setup tool to make sure your database has the proper tables
#and columns.

# ----------------------------- MAIN FUNCTION -----------------------------
def main():
    print("Creating tables...")               # Notify user before table creation
    Base.metadata.create_all(bind=engine)     # Create all tables defined in models
    print("Done.")                            # Confirm completion

# ----------------------------- EXECUTION ENTRY POINT -----------------------------
if __name__ == "__main__":
    main()  # Run main() only when executed directly
