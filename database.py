# ----------------------------- IMPORTS -----------------------------
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ----------------------------- DATABASE CONFIGURATION -----------------------------
# Replace username and password with your PostgreSQL credentials
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:databasepw@localhost:5432/moviedb"

# ----------------------------- ENGINE SETUP -----------------------------
# Connects SQLAlchemy to the PostgreSQL database
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# ----------------------------- SESSION SETUP -----------------------------
# Creates a session to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ----------------------------- BASE MODEL -----------------------------
# Base class for models (Movie, Director, Genre, etc.)
Base = declarative_base()

# ----------------------------- CONNECTION TEST -----------------------------
if __name__ == "__main__":
    try:
        with engine.connect() as conn:
            print("✅ Connection successful!")
    except Exception as e:
        print("❌ Connection failed:", e)
