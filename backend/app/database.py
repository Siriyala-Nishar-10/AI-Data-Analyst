import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/ai_data_analyst",
)

# pool_pre_ping helps avoid stale connection errors
# after the database has been idle.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def init_db() -> None:
    """
    Create tables if they don't exist and make sure the
    persistent file_content column exists.
    """

    # Import models so SQLAlchemy knows about the Dataset table.
    from app import models  # noqa: F401

    # Create the table if it doesn't already exist.
    Base.metadata.create_all(bind=engine)

    # Add file_content to an existing database.
    # This is safe to run every time the application starts.
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                ALTER TABLE datasets
                ADD COLUMN IF NOT EXISTS file_content TEXT
                """
            )
        )