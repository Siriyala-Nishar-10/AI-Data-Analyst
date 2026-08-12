from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    filename = Column(String, nullable=False)

    # Kept for backward compatibility with existing records.
    file_path = Column(String, nullable=False, default="")

    # Persistent CSV content stored in PostgreSQL.
    # The content is stored as Base64 text.
    file_content = Column(Text, nullable=True)

    row_count = Column(Integer, nullable=True)
    column_count = Column(Integer, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())