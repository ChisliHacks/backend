from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependencies import get_db
from app.crud import job as job_crud
from app.schemas.job import JobCreate, JobUpdate, JobResponse, JobListResponse, JobSearchResponse

router = APIRouter()


@router.post("/", response_model=JobResponse)
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db)
):
    """Create a new job"""
    # Check if job with same position and company already exists
    existing_job = job_crud.get_job_by_position_company(db, job.position, job.company)
    if existing_job:
        raise HTTPException(status_code=400, detail="Job with this position and company already exists")
    
    return job_crud.create_job(db=db, job=job)


@router.get("/", response_model=List[JobListResponse])
def read_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    company: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    experience_level: Optional[str] = Query(None),
    remote_option: Optional[bool] = Query(None),
    is_active: Optional[bool] = Query(None),
    recruiter_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get jobs with optional filtering"""
    jobs = job_crud.get_jobs(
        db=db, 
        skip=skip, 
        limit=limit,
        company=company,
        location=location,
        job_type=job_type,
        experience_level=experience_level,
        remote_option=remote_option,
        is_active=is_active,
        recruiter_id=recruiter_id
    )
    return jobs


@router.get("/active", response_model=List[JobListResponse])
def read_active_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get only active jobs"""
    jobs = job_crud.get_active_jobs(db=db, skip=skip, limit=limit)
    return jobs


@router.get("/remote", response_model=List[JobListResponse])
def read_remote_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get remote jobs"""
    jobs = job_crud.get_remote_jobs(db=db, skip=skip, limit=limit)
    return jobs


@router.get("/search", response_model=List[JobSearchResponse])
def search_jobs(
    q: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Search jobs by position, company, or description"""
    jobs = job_crud.search_jobs(db=db, search_term=q, skip=skip, limit=limit)
    return jobs


@router.get("/company/{company}", response_model=List[JobListResponse])
def read_jobs_by_company(
    company: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get jobs by company"""
    jobs = job_crud.get_jobs_by_company(db=db, company=company, skip=skip, limit=limit)
    return jobs


@router.get("/location/{location}", response_model=List[JobListResponse])
def read_jobs_by_location(
    location: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get jobs by location"""
    jobs = job_crud.get_jobs_by_location(db=db, location=location, skip=skip, limit=limit)
    return jobs


@router.get("/type/{job_type}", response_model=List[JobListResponse])
def read_jobs_by_type(
    job_type: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get jobs by type (full-time, part-time, contract, internship)"""
    jobs = job_crud.get_jobs_by_type(db=db, job_type=job_type, skip=skip, limit=limit)
    return jobs


@router.get("/experience/{experience_level}", response_model=List[JobListResponse])
def read_jobs_by_experience_level(
    experience_level: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get jobs by experience level"""
    jobs = job_crud.get_jobs_by_experience_level(db=db, experience_level=experience_level, skip=skip, limit=limit)
    return jobs


@router.get("/recruiter/{recruiter_id}", response_model=List[JobListResponse])
def read_jobs_by_recruiter(
    recruiter_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get jobs by recruiter"""
    jobs = job_crud.get_jobs_by_recruiter(db=db, recruiter_id=recruiter_id, skip=skip, limit=limit)
    return jobs


@router.get("/statistics")
def get_job_statistics(db: Session = Depends(get_db)):
    """Get job statistics including counts by type and experience level"""
    stats = job_crud.get_job_statistics(db=db)
    return stats


@router.get("/count")
def count_jobs(
    company: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    experience_level: Optional[str] = Query(None),
    remote_option: Optional[bool] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Count total jobs with optional filtering"""
    count = job_crud.count_jobs(
        db=db, 
        company=company,
        location=location,
        job_type=job_type,
        experience_level=experience_level,
        remote_option=remote_option,
        is_active=is_active
    )
    return {"count": count}


@router.get("/{job_id}", response_model=JobResponse)
def read_job(job_id: int, db: Session = Depends(get_db)):
    """Get a specific job by ID"""
    job = job_crud.get_job(db=db, job_id=job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_update: JobUpdate,
    db: Session = Depends(get_db)
):
    """Update a job"""
    job = job_crud.update_job(db=db, job_id=job_id, job_update=job_update)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.patch("/{job_id}/activate", response_model=JobResponse)
def activate_job(job_id: int, db: Session = Depends(get_db)):
    """Activate a job"""
    job = job_crud.activate_job(db=db, job_id=job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.patch("/{job_id}/deactivate", response_model=JobResponse)
def deactivate_job(job_id: int, db: Session = Depends(get_db)):
    """Deactivate a job"""
    job = job_crud.deactivate_job(db=db, job_id=job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    """Delete a job"""
    job = job_crud.delete_job(db=db, job_id=job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Job deleted successfully"}
