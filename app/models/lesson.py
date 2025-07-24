from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)  # Temporary field for backward compatibility
    category = Column(String, index=True, nullable=False)
    filename = Column(String, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    # beginner, intermediate, advanced
    difficulty_level = Column(String, default="beginner")
    is_published = Column(Boolean, default=False)

    # If you want to associate lessons with users (instructors)
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to user (instructor)
    # instructor = relationship("User", back_populates="lessons")
