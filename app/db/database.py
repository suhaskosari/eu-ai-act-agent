from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Creates all tables in PostgreSQL if they don't exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Returns a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()