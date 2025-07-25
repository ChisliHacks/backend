from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.models.user import User
from app.models.lesson import Lesson, lesson_related_job_association
from app.models.related_job import RelatedJob
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.auth import UserRegister
from app.core.auth import hash_password, verify_password


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate):
    hashed_password = hash_password(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        lessons_completed=0,
        total_lesson_score=0
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def register_user(db: Session, user: UserRegister):
    """Register a new user with proper validation"""
    hashed_password = hash_password(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        lessons_completed=0,
        total_lesson_score=0
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str):
    """Authenticate user by username and password"""
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def update_user(db: Session, user_id: int, user_update: UserUpdate):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        db.commit()
        db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user


def complete_lesson(db: Session, user_id: int, lesson_score: int = 0):
    """
    Mark a lesson as completed for a user and update their statistics
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db_user.lessons_completed += 1
        db_user.total_lesson_score += lesson_score
        db.commit()
        db.refresh(db_user)
    return db_user


def reset_user_progress(db: Session, user_id: int):
    """
    Reset a user's lesson progress (lessons_completed and total_lesson_score to 0)
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db_user.lessons_completed = 0
        db_user.total_lesson_score = 0
        db.commit()
        db.refresh(db_user)
    return db_user


def get_user_stats(db: Session, user_id: int):
    """
    Get user statistics including lessons completed and total score
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        return {
            "user_id": db_user.id,
            "username": db_user.username,
            "lessons_completed": db_user.lessons_completed,
            "total_lesson_score": db_user.total_lesson_score,
            "average_score": db_user.total_lesson_score / db_user.lessons_completed if db_user.lessons_completed > 0 else 0
        }
    return None


def get_top_performers(db: Session, limit: int = 10):
    """
    Get top performers sorted by total lesson score, then by lessons completed
    """
    users = db.query(User).filter(
        User.is_active == True,
        User.lessons_completed > 0
    ).order_by(
        User.total_lesson_score.desc(),
        User.lessons_completed.desc()
    ).limit(limit).all()

    result = []
    for user in users:
        result.append({
            "id": user.id,
            "username": user.username,
            "lessons_completed": user.lessons_completed,
            "total_lesson_score": user.total_lesson_score,
            "average_score": user.total_lesson_score / user.lessons_completed if user.lessons_completed > 0 else 0,
            "created_at": user.created_at.isoformat() if user.created_at else None
        })

    return result


def get_top_performers_by_related_jobs(db: Session, limit_per_job: int = 5):
    """
    Get top performers grouped by related job positions
    Returns a dictionary with job positions as keys and top performers as values
    """
    # First, get all unique related job positions
    related_jobs = db.query(RelatedJob).filter(
        RelatedJob.is_active == True).all()

    result = {}

    for job in related_jobs:
        # For each job, find users who have completed lessons related to this job
        # and calculate their performance in job-related lessons

        # Get lessons related to this job
        job_lessons = db.query(Lesson).join(
            lesson_related_job_association
        ).filter(
            lesson_related_job_association.c.related_job_id == job.id
        ).all()

        if not job_lessons:
            continue

        lesson_ids = [lesson.id for lesson in job_lessons]

        # This is a simplified approach - in a real implementation, you'd need
        # a user_lesson_completions table to track which users completed which lessons
        # For now, we'll use the general user stats but group by job

        performers = []
        users = db.query(User).filter(
            User.is_active == True,
            User.lessons_completed > 0
        ).order_by(
            User.total_lesson_score.desc(),
            User.lessons_completed.desc()
        ).limit(limit_per_job * 2).all()  # Get more to filter

        for user in users:
            # Calculate job-specific score (simplified - in real implementation,
            # this would be based on actual lessons completed for this job)
            job_score = user.total_lesson_score * \
                (len(job_lessons) / max(user.lessons_completed, 1))

            performers.append({
                "id": user.id,
                "username": user.username,
                "lessons_completed": user.lessons_completed,
                "total_lesson_score": user.total_lesson_score,
                "job_specific_score": round(job_score, 1),
                "average_score": user.total_lesson_score / user.lessons_completed if user.lessons_completed > 0 else 0,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "related_lessons_count": len(job_lessons)
            })

        # Sort by job-specific score and limit
        performers.sort(key=lambda x: x["job_specific_score"], reverse=True)
        performers = performers[:limit_per_job]

        if performers:  # Only include jobs that have performers
            result[job.position] = {
                "job_info": {
                    "id": job.id,
                    "position": job.position,
                    "company": job.company,
                    "job_type": job.job_type,
                    "experience_level": job.experience_level,
                    "industry": job.industry,
                    "related_lessons_count": len(job_lessons)
                },
                "top_performers": performers
            }

    return result


def get_user_best_job_performance(db: Session, user_id: int):
    """Get the user's best performing related job based on their overall lesson scores and job preferences"""

    # Get the user first to check if they have any lesson activity
    user = get_user(db, user_id)
    if not user or user.lessons_completed == 0:
        return None

    # Get all jobs and their related lesson counts, ordered by number of related lessons (descending)
    # This will show the job with the most learning content available as their "best match"
    jobs_with_lessons = db.query(
        RelatedJob,
        func.count(lesson_related_job_association.c.lesson_id).label(
            'related_lessons_count')
    ).join(
        lesson_related_job_association, RelatedJob.id == lesson_related_job_association.c.related_job_id
    ).group_by(
        RelatedJob.id
    ).order_by(
        desc('related_lessons_count')
    ).first()

    if not jobs_with_lessons:
        return None

    job, related_lessons_count = jobs_with_lessons

    # Calculate user's performance metrics for this job
    # Since we don't have detailed lesson tracking, we'll estimate based on overall performance
    # Estimate 70% is job-related
    estimated_job_score = int(user.total_lesson_score * 0.7)
    estimated_completed_lessons = max(
        1, int(user.lessons_completed * 0.6))  # Estimate 60% are job-related

    return {
        "job_info": {
            "id": job.id,
            "position": job.position,
            "company": job.company,
            "job_type": job.job_type,
            "experience_level": job.experience_level,
            "industry": job.industry,
        },
        "performance": {
            "total_job_score": estimated_job_score,
            "completed_lessons": estimated_completed_lessons,
            "average_score": user.total_lesson_score / user.lessons_completed if user.lessons_completed > 0 else 0,
            "related_lessons_available": related_lessons_count
        }
    }
