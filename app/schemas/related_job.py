from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RelatedJobBase(BaseModel):
    position: str
    company: Optional[str] = None
    description: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    industry: Optional[str] = None
    skills_required: Optional[str] = None


class RelatedJobCreate(RelatedJobBase):
    pass


class RelatedJobUpdate(BaseModel):
    position: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    industry: Optional[str] = None
    skills_required: Optional[str] = None
    is_active: Optional[bool] = None


class RelatedJobResponse(RelatedJobBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RelatedJobBasic(BaseModel):
    id: int
    position: str
    company: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None

    class Config:
        from_attributes = True
