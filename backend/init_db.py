"""Create database tables from SQLAlchemy models."""

from app.database import Base, engine
from app.models import models  # noqa: F401 - imports models into Base.metadata


def create_tables():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Done. Tables:")
    for table_name in Base.metadata.tables.keys():
        print(f"   - {table_name}")


if __name__ == "__main__":
    create_tables()
