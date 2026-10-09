"""
database.py
-----------
SQLAlchemy engine + session banata hai.

NOTE: Module 1 document mein team ko PostgreSQL ya MongoDB me se
ek choose karne ko kaha gaya hai. Yahan SQLite default rakha hai
(zero setup, turant chal jaata hai), lekin SQLAlchemy use karne ki
wajah se sirf DATABASE_URL badalke PostgreSQL par switch karna aasan hai:

    DATABASE_URL=postgresql://user:password@localhost:5432/clipmind

Agar team MongoDB choose karti hai, to models.py ko SQLAlchemy models
ki jagah Pydantic + pymongo/motor documents se replace karna hoga.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    # SQLite ko multi-thread FastAPI ke saath chalane ke liye zaroori
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Har request ke liye ek DB session deta hai, aur end mein close kar deta hai."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
