"""
Database connection settings.

Internal structure is intentionally English: variable names, database tables,
ORM models, schemas and API routes. User-facing UI labels/messages can remain
Turkish in the frontend layer.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

DATABASE_URL = settings.database_url
AUTH_ENABLED = settings.auth_enabled

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
