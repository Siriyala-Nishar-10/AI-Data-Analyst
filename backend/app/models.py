from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.database import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    row_count = Column(Integer, nullable=True)
    column_count = Column(Integer, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
