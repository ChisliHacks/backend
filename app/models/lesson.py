from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


# Association table for many-to-many relationship between lessons and related jobs
lesson_related_job_association = Table(
    'lesson_related_job_relations',
    Base.metadata,
    Column('lesson_id', Integer, ForeignKey('lessons.id'), primary_key=True),
    Column('related_job_id', Integer, ForeignKey(
        'related_jobs.id'), primary_key=True)
)


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False, default="")
    summary = Column(Text, nullable=False, default="")
    # Temporary field for backward compatibility
    content = Column(Text, nullable=False, default="")
    category = Column(String, index=True, nullable=False)
    filename = Column(String, nullable=False, default="")
    duration_minutes = Column(Integer, nullable=False, default=0)
    # beginner, intermediate, advanced
    difficulty_level = Column(String, default="beginner", nullable=False)
    lesson_score = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to user (instructor)
    # instructor = relationship("User", back_populates="lessons")

    # Many-to-many relationship with related jobs
    related_jobs = relationship(
        "RelatedJob",
        secondary=lesson_related_job_association,
        back_populates="related_lessons"
    )
