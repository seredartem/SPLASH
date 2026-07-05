from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.database import Base

class ClassModel(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description =  Column(String, nullable=True)
    level = Column(String, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)