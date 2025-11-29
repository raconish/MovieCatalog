# ----------------------------- IMPORTS -----------------------------
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ----------------------------- DATABASE CONFIGURATION -----------------------------
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:databasepw@localhost:5432/moviedb"

# ----------------------------- ENGINE SETUP -----------------------------
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# ----------------------------- SESSION SETUP -----------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ----------------------------- BASE MODEL -----------------------------
Base = declarative_base()

# ----------------------------- CONNECTION TEST -----------------------------
if __name__ == "__main__":
    try:
        with engine.connect() as conn:
            print("✅ Connection successful!")
    except Exception as e:
        print("❌ Connection failed:", e)
