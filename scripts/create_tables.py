import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from app.db.database import Base, engine
from app.models import tables


def main():
    print("Database URL:", engine.url)
    print("Tables detected by SQLAlchemy:", Base.metadata.tables.keys())

    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Done. Tables created.")


if __name__ == "__main__":
    main()