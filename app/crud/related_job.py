from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.related_job import RelatedJob
from app.schemas.related_job import RelatedJobCreate, RelatedJobUpdate


def get_related_job(db: Session, related_job_id: int) -> Optional[RelatedJob]:
    """Get a related job by ID"""
    return db.query(RelatedJob).filter(RelatedJob.id == related_job_id).first()


def get_related_job_by_position(db: Session, position: str, company: str = None) -> Optional[RelatedJob]:
    """Get a related job by position and optionally company"""
    query = db.query(RelatedJob).filter(
        RelatedJob.position.ilike(f"%{position}%"))
    if company:
        query = query.filter(RelatedJob.company.ilike(f"%{company}%"))
    return query.first()


def get_related_jobs(db: Session, skip: int = 0, limit: int = 100,
                     position: str = None, company: str = None,
                     job_type: str = None, is_active: bool = True) -> List[RelatedJob]:
    """Get related jobs with optional filtering"""
    query = db.query(RelatedJob)

    if is_active is not None:
        query = query.filter(RelatedJob.is_active == is_active)
    if position:
        query = query.filter(RelatedJob.position.ilike(f"%{position}%"))
    if company:
        query = query.filter(RelatedJob.company.ilike(f"%{company}%"))
    if job_type:
        query = query.filter(RelatedJob.job_type.ilike(f"%{job_type}%"))

    return query.offset(skip).limit(limit).all()


def create_related_job(db: Session, related_job: RelatedJobCreate) -> RelatedJob:
    """Create a new related job"""
    db_related_job = RelatedJob(**related_job.dict())
    db.add(db_related_job)
    db.commit()
    db.refresh(db_related_job)
    return db_related_job


def update_related_job(db: Session, related_job_id: int, related_job_update: RelatedJobUpdate) -> Optional[RelatedJob]:
    """Update an existing related job"""
    db_related_job = db.query(RelatedJob).filter(
        RelatedJob.id == related_job_id).first()
    if db_related_job:
        update_data = related_job_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_related_job, field, value)
        db.commit()
        db.refresh(db_related_job)
    return db_related_job


def delete_related_job(db: Session, related_job_id: int) -> bool:
    """Delete a related job (soft delete by setting is_active=False)"""
    db_related_job = db.query(RelatedJob).filter(
        RelatedJob.id == related_job_id).first()
    if db_related_job:
        db_related_job.is_active = False
        db.commit()
        return True
    return False


def find_or_create_related_job(db: Session, position: str, company: str = None) -> RelatedJob:
    """Find an existing related job or create a new one"""
    # Try to find existing job
    existing_job = get_related_job_by_position(db, position, company)
    if existing_job:
        return existing_job

    # Create new job if not found
    new_job_data = RelatedJobCreate(
        position=position,
        company=company
    )
    return create_related_job(db, new_job_data)
