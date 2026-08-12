import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/ai_data_analyst",
)

# pool_pre_ping avoids stale-connection errors after the DB has been idle
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db() -> None:
    """Create all tables that don't exist yet. Safe to call on every startup."""
    from app import models  # noqa: F401 (ensures models are registered on Base)

    Base.metadata.create_all(bind=engine)
