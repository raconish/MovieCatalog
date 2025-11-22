# ----------------------------- IMPORTS -----------------------------
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

#NTS: these imports bring in the tools you need to connect Python to your database and define models.
#NTS: create_engine → connects SQLAlchemy to your database (PostgreSQL in this case).
#NTS: sessionmaker → creates a session factory so you can easily talk to the database.
#NTS: declarative_base → lets you define your models (like Movie, Director, etc.) as Python classes.

# ----------------------------- DATABASE CONFIGURATION -----------------------------
#NTS: Replace username and password with your PostgreSQL credentials
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:databasepw@localhost:5432/moviedb"

#NTS: This is your connection string. It tells SQLAlchemy where and how to connect.
#NTS: dialect → postgresql 

# ----------------------------- ENGINE SETUP -----------------------------
# Connects SQLAlchemy to the PostgreSQL database
engine = create_engine(SQLALCHEMY_DATABASE_URL)

#NTS: Think of the engine as the “motor” that powers all communication with the database.
#NTS: It doesn’t hold a connection open all the time — it manages them efficiently under the hood.

# ----------------------------- SESSION SETUP -----------------------------
# Creates a session to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#NTS: This creates a session factory — like a machine that produces “database sessions.”

# ----------------------------- BASE MODEL -----------------------------
# Base class for models (Movie, Director, Genre, etc.)
Base = declarative_base()

#NTS: This creates a base class that all your models will inherit from.

# ----------------------------- CONNECTION TEST -----------------------------
if __name__ == "__main__":
    try:
        with engine.connect() as conn:
            print("✅ Connection successful!")
    except Exception as e:
        print("❌ Connection failed:", e)

#NTS: Every .py file in Python has a hidden variable called __name__
# If the fileIf you run the file directly, it will be "__main__". 
# But if you import the file from another file (e.g. import database), it will show the file's name, 
# without py (e.g. database). What this is saying is: Only run the next block if this file is the one
# the user ran directly, not if it’s just being imported by another file.
