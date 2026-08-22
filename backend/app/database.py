"""
database.py
------------
Sets up the connection to the PostgreSQL database (clipmind_db) using SQLAlchemy.

Exposes:
- engine        : the actual DB connection
- SessionLocal  : factory that creates new DB sessions
- Base          : declarative base class for ORM models (used in models.py)
- get_db()      : FastAPI dependency that provides a session per request
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path
from dotenv import load_dotenv

# Load variables from backend/.env regardless of current working directory
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")


if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Make sure you have a .env file "
        "with DATABASE_URL defined (see .env.example)."
    )

# The engine manages the actual connection pool to PostgreSQL
engine = create_engine(DATABASE_URL)

# Each instance of SessionLocal is a new database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that our ORM models (e.g. User) will inherit from
Base = declarative_base()


def get_db():
    """
    FastAPI dependency.
    Opens a new DB session for a request, yields it to the route,
    and always closes it afterward (even if an error occurs).

    Usage in a route:
        def some_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()