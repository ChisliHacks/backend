from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class JobBase(BaseModel):
    position: str
    company: str
    description: Optional[str] = None
    job_criteria: str
    location: Optional[str] = None
    salary_range: Optional[str] = None
    job_type: Optional[str] = "full-time"
    remote_option: Optional[bool] = False
    experience_level: Optional[str] = "entry"
    is_active: Optional[bool] = True


class JobCreate(JobBase):
    recruiter_id: Optional[int] = None


class JobUpdate(BaseModel):
    position: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    job_criteria: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    job_type: Optional[str] = None
    remote_option: Optional[bool] = None
    experience_level: Optional[str] = None
    is_active: Optional[bool] = None
    recruiter_id: Optional[int] = None


class JobResponse(JobBase):
    id: int
    recruiter_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    id: int
    position: str
    company: str
    location: Optional[str] = None
    salary_range: Optional[str] = None
    job_type: str
    remote_option: bool
    experience_level: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class JobSearchResponse(BaseModel):
    id: int
    position: str
    company: str
    description: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    job_type: str
    remote_option: bool
    experience_level: str
    created_at: datetime

    class Config:
        from_attributes = True
