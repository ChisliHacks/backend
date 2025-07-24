from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate


def get_job(db: Session, job_id: int) -> Optional[Job]:
    """Get a single job by ID"""
    return db.query(Job).filter(Job.id == job_id).first()


def get_job_by_position_company(db: Session, position: str, company: str) -> Optional[Job]:
    """Get a job by position and company combination"""
    return db.query(Job).filter(Job.position == position, Job.company == company).first()


def get_jobs(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    company: Optional[str] = None,
    location: Optional[str] = None,
    job_type: Optional[str] = None,
    experience_level: Optional[str] = None,
    remote_option: Optional[bool] = None,
    is_active: Optional[bool] = None,
    recruiter_id: Optional[int] = None
) -> List[Job]:
    """Get multiple jobs with optional filtering"""
    query = db.query(Job)
    
    if company:
        query = query.filter(Job.company.ilike(f"%{company}%"))
    
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    
    if job_type:
        query = query.filter(Job.job_type == job_type)
    
    if experience_level:
        query = query.filter(Job.experience_level == experience_level)
    
    if remote_option is not None:
        query = query.filter(Job.remote_option == remote_option)
    
    if is_active is not None:
        query = query.filter(Job.is_active == is_active)
    
    if recruiter_id:
        query = query.filter(Job.recruiter_id == recruiter_id)
    
    return query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()


def get_active_jobs(db: Session, skip: int = 0, limit: int = 100) -> List[Job]:
    """Get only active jobs"""
    return db.query(Job).filter(Job.is_active == True).order_by(Job.created_at.desc()).offset(skip).limit(limit).all()


def get_jobs_by_company(db: Session, company: str, skip: int = 0, limit: int = 100) -> List[Job]:
    """Get jobs by company (case-insensitive search)"""
    return db.query(Job).filter(Job.company.ilike(f"%{company}%")).order_by(Job.created_at.desc()).offset(skip).limit(limit).all()


def get_jobs_by_location(db: Session, location: str, skip: int = 0, limit: int = 100) -> List[Job]:
    """Get jobs by location (case-insensitive search)"""
    return db.query(Job).filter(Job.location.ilike(f"%{location}%")).order_by(Job.created_at.desc()).offset(skip).limit(limit).all()


def get_jobs_by_recruiter(db: Session, recruiter_id: int, skip: int = 0, limit: int = 100) -> List[Job]:
    """Get jobs by recruiter"""
    return db.query(Job).filter(Job.recruiter_id == recruiter_id).order_by(Job.created_at.desc()).offset(skip).limit(limit).all()


def get_remote_jobs(db: Session, skip: int = 0, limit: int = 100) -> List[Job]:
    """Get remote jobs"""
    return db.query(Job).filter(Job.remote_option == True, Job.is_active == True).order_by(Job.created_at.desc()).offset(skip).limit(limit).all()


def get_jobs_by_type(db: Session, job_type: str, skip: int = 0, limit: int = 100) -> List[Job]:
    """Get jobs by type (full-time, part-time, contract, internship)"""
    return db.query(Job).filter(Job.job_type == job_type).order_by(Job.created_at.desc()).offset(skip).limit(limit).all()


def get_jobs_by_experience_level(db: Session, experience_level: str, skip: int = 0, limit: int = 100) -> List[Job]:
    """Get jobs by experience level"""
    return db.query(Job).filter(Job.experience_level == experience_level).order_by(Job.created_at.desc()).offset(skip).limit(limit).all()


def create_job(db: Session, job: JobCreate) -> Job:
    """Create a new job"""
    db_job = Job(
        position=job.position,
        company=job.company,
        description=job.description,
        job_criteria=job.job_criteria,
        location=job.location,
        salary_range=job.salary_range,
        job_type=job.job_type,
        remote_option=job.remote_option,
        experience_level=job.experience_level,
        is_active=job.is_active,
        recruiter_id=job.recruiter_id
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


def update_job(db: Session, job_id: int, job_update: JobUpdate) -> Optional[Job]:
    """Update an existing job"""
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if db_job:
        update_data = job_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_job, field, value)
        db.commit()
        db.refresh(db_job)
    return db_job


def delete_job(db: Session, job_id: int) -> Optional[Job]:
    """Delete a job"""
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if db_job:
        db.delete(db_job)
        db.commit()
    return db_job


def activate_job(db: Session, job_id: int) -> Optional[Job]:
    """Activate a job (set is_active to True)"""
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if db_job:
        db_job.is_active = True
        db.commit()
        db.refresh(db_job)
    return db_job


def deactivate_job(db: Session, job_id: int) -> Optional[Job]:
    """Deactivate a job (set is_active to False)"""
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if db_job:
        db_job.is_active = False
        db.commit()
        db.refresh(db_job)
    return db_job


def search_jobs(db: Session, search_term: str, skip: int = 0, limit: int = 100) -> List[Job]:
    """Search jobs by position, company, or description"""
    return db.query(Job).filter(
        Job.position.ilike(f"%{search_term}%") | 
        Job.company.ilike(f"%{search_term}%") |
        Job.description.ilike(f"%{search_term}%")
    ).filter(Job.is_active == True).order_by(Job.created_at.desc()).offset(skip).limit(limit).all()


def count_jobs(
    db: Session, 
    company: Optional[str] = None,
    location: Optional[str] = None,
    job_type: Optional[str] = None,
    experience_level: Optional[str] = None,
    remote_option: Optional[bool] = None,
    is_active: Optional[bool] = None
) -> int:
    """Count total jobs with optional filtering"""
    query = db.query(Job)
    
    if company:
        query = query.filter(Job.company.ilike(f"%{company}%"))
    
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    
    if job_type:
        query = query.filter(Job.job_type == job_type)
    
    if experience_level:
        query = query.filter(Job.experience_level == experience_level)
    
    if remote_option is not None:
        query = query.filter(Job.remote_option == remote_option)
    
    if is_active is not None:
        query = query.filter(Job.is_active == is_active)
    
    return query.count()


def get_job_statistics(db: Session) -> dict:
    """Get job statistics"""
    total_jobs = db.query(Job).count()
    active_jobs = db.query(Job).filter(Job.is_active == True).count()
    remote_jobs = db.query(Job).filter(Job.remote_option == True, Job.is_active == True).count()
    
    job_types = db.query(Job.job_type, db.func.count(Job.id)).filter(Job.is_active == True).group_by(Job.job_type).all()
    experience_levels = db.query(Job.experience_level, db.func.count(Job.id)).filter(Job.is_active == True).group_by(Job.experience_level).all()
    
    return {
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "remote_jobs": remote_jobs,
        "job_types": dict(job_types),
        "experience_levels": dict(experience_levels)
    }
