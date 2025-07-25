from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class RelatedJob(Base):
    __tablename__ = "related_jobs"

    id = Column(Integer, primary_key=True, index=True)
    position = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    # e.g., "Full-time", "Part-time", "Contract"
    job_type = Column(String(100), nullable=True)
    # e.g., "Entry-level", "Mid-level", "Senior"
    experience_level = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    # JSON string or comma-separated
    skills_required = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Many-to-many relationship back to lessons
    related_lessons = relationship(
        "Lesson",
        secondary="lesson_related_job_relations",
        back_populates="related_jobs"
    )

    def __repr__(self):
        return f"<RelatedJob(id={self.id}, position='{self.position}', company='{self.company}')>"
