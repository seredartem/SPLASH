from app.database import Base
from sqlalchemy import Column, Integer, Date, Time, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    max_places = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False) 
    created_at = Column(DateTime, server_default=func.now(), nullable=False)