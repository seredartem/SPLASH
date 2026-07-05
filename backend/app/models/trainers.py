from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.database import Base
from sqlalchemy.sql import func


class Trainer(Base):
    __tablename__ = "trainers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    bio = Column(String, nullable=True)
    specialization = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False) 
    created_at = Column(DateTime, server_default=func.now(), nullable=False)