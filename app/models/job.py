from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    position = Column(String, index=True, nullable=False)
    company = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    job_criteria = Column(String, nullable=False)
    location = Column(String, nullable=True)
    salary_range = Column(String, nullable=True)
    # full-time, part-time, contract, internship
    job_type = Column(String, default="full-time")
    remote_option = Column(Boolean, default=False)
    # entry, mid, senior, lead
    experience_level = Column(String, default="entry")
    is_active = Column(Boolean, default=True)

    # If you want to associate jobs with users (recruiters)
    recruiter_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to user (recruiter)
    # recruiter = relationship("User", back_populates="jobs")

    # Note: Job model no longer has direct relationship with lessons
    # Use RelatedJob model for lesson-job associations
