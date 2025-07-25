from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# Forward reference for RelatedJob to avoid circular imports
class RelatedJobBasic(BaseModel):
    id: int
    position: str
    company: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None

    class Config:
        from_attributes = True


class LessonBase(BaseModel):
    title: str
    description: Optional[str] = None
    summary: Optional[str] = None
    category: str
    filename: Optional[str] = None
    duration_minutes: Optional[int] = None
    difficulty_level: Optional[str] = "beginner"
    is_published: Optional[bool] = False


class LessonCreate(LessonBase):
    instructor_id: Optional[int] = None
    related_job_ids: Optional[List[int]] = []
    # New field for job position strings that will be matched/created
    related_job_positions: Optional[List[str]] = []


class LessonUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    filename: Optional[str] = None
    duration_minutes: Optional[int] = None
    difficulty_level: Optional[str] = None
    is_published: Optional[bool] = None
    instructor_id: Optional[int] = None
    related_job_ids: Optional[List[int]] = None
    # New field for job position strings that will be matched/created
    related_job_positions: Optional[List[str]] = []


class LessonResponse(LessonBase):
    id: int
    instructor_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    related_jobs: Optional[List[RelatedJobBasic]] = []

    class Config:
        from_attributes = True


class LessonListResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    summary: Optional[str] = None
    category: str
    filename: Optional[str] = None
    duration_minutes: Optional[int] = None
    difficulty_level: str
    is_published: bool
    created_at: datetime
    related_jobs: Optional[List[RelatedJobBasic]] = []

    class Config:
        from_attributes = True
