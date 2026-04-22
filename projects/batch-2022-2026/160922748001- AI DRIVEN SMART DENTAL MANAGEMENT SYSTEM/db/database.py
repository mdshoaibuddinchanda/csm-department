# db/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# Example DATABASE_URL:
# postgresql://user:password@host:port/dbname

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # avoids stale connections
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()
