from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.lesson import Lesson
from app.models.related_job import RelatedJob
from app.models.user import User
from app.schemas.lesson import LessonCreate, LessonUpdate
from app.crud.related_job import find_or_create_related_job


def find_or_create_related_jobs_from_positions(db: Session, job_positions: List[str]) -> List[RelatedJob]:
    """
    Find or create related jobs from a list of job position strings
    """
    related_jobs = []
    for position in job_positions:
        if position and position.strip():
            related_job = find_or_create_related_job(db, position.strip())
            related_jobs.append(related_job)
    return related_jobs


def get_lesson(db: Session, lesson_id: int) -> Optional[Lesson]:
    """Get a single lesson by ID"""
    return db.query(Lesson).filter(Lesson.id == lesson_id).first()


def get_lesson_by_title(db: Session, title: str) -> Optional[Lesson]:
    """Get a lesson by title"""
    return db.query(Lesson).filter(Lesson.title == title).first()


def get_lessons(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    difficulty_level: Optional[str] = None
) -> List[Lesson]:
    """Get multiple lessons with optional filtering"""
    query = db.query(Lesson)

    if category:
        query = query.filter(Lesson.category.ilike(f"%{category}%"))
    if difficulty_level:
        query = query.filter(Lesson.difficulty_level == difficulty_level)

    return query.offset(skip).limit(limit).all()


def get_published_lessons(db: Session, skip: int = 0, limit: int = 100) -> List[Lesson]:
    """Get all lessons (formerly published lessons, now all lessons since is_published is removed)"""
    return db.query(Lesson).offset(skip).limit(limit).all()


def create_lesson(db: Session, lesson: LessonCreate) -> Lesson:
    """Create a new lesson"""
    lesson_data = lesson.dict(
        exclude={'related_job_ids', 'related_job_positions'})

    # Validate lesson_score if provided
    if lesson_data.get('lesson_score') is not None and lesson_data['lesson_score'] < 0:
        raise ValueError("Lesson score cannot be negative")

    db_lesson = Lesson(**lesson_data)

    db.add(db_lesson)
    db.flush()  # Flush to get the lesson ID

    # Handle related jobs
    all_related_jobs = []

    # Add jobs from provided IDs
    if lesson.related_job_ids:
        existing_jobs = db.query(RelatedJob).filter(
            RelatedJob.id.in_(lesson.related_job_ids)).all()
        all_related_jobs.extend(existing_jobs)

    # Find or create jobs from position strings
    if lesson.related_job_positions:
        new_jobs = find_or_create_related_jobs_from_positions(
            db, lesson.related_job_positions)
        all_related_jobs.extend(new_jobs)

    # Remove duplicates and assign to lesson
    if all_related_jobs:
        unique_jobs = {job.id: job for job in all_related_jobs}.values()
        db_lesson.related_jobs = list(unique_jobs)

    db.commit()
    db.refresh(db_lesson)
    return db_lesson


def update_lesson(db: Session, lesson_id: int, lesson_update: LessonUpdate) -> Optional[Lesson]:
    """Update an existing lesson"""
    db_lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if db_lesson:
        update_data = lesson_update.dict(exclude_unset=True)

        # Handle related jobs separately
        related_job_ids = update_data.pop('related_job_ids', None)
        related_job_positions = update_data.pop('related_job_positions', None)

        # Update other fields
        for field, value in update_data.items():
            setattr(db_lesson, field, value)

        # Update related jobs if provided
        if related_job_ids is not None or related_job_positions is not None:
            all_related_jobs = []

            # Add jobs from provided IDs
            if related_job_ids:
                existing_jobs = db.query(RelatedJob).filter(
                    RelatedJob.id.in_(related_job_ids)).all()
                all_related_jobs.extend(existing_jobs)

            # Find or create jobs from position strings
            if related_job_positions:
                new_jobs = find_or_create_related_jobs_from_positions(
                    db, related_job_positions)
                all_related_jobs.extend(new_jobs)

            # Update related jobs
            if all_related_jobs:
                # Remove duplicates
                unique_jobs = {
                    job.id: job for job in all_related_jobs}.values()
                db_lesson.related_jobs = list(unique_jobs)
            else:
                # Clear all related jobs if empty lists provided
                db_lesson.related_jobs = []

        db.commit()
        db.refresh(db_lesson)
    return db_lesson


def delete_lesson(db: Session, lesson_id: int) -> bool:
    """Delete a lesson"""
    db_lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if db_lesson:
        db.delete(db_lesson)
        db.commit()
        return True
    return False


def search_lessons(db: Session, search_term: str, skip: int = 0, limit: int = 100) -> List[Lesson]:
    """Search lessons by title, description, or category"""
    search_pattern = f"%{search_term}%"
    return db.query(Lesson).filter(
        (Lesson.title.ilike(search_pattern)) |
        (Lesson.description.ilike(search_pattern)) |
        (Lesson.category.ilike(search_pattern))
    ).offset(skip).limit(limit).all()


def get_lessons_by_category(db: Session, category: str, skip: int = 0, limit: int = 100) -> List[Lesson]:
    """Get lessons by category"""
    return db.query(Lesson).filter(Lesson.category.ilike(f"%{category}%")).offset(skip).limit(limit).all()


def get_lessons_by_difficulty(db: Session, difficulty_level: str, skip: int = 0, limit: int = 100) -> List[Lesson]:
    """Get lessons by difficulty level"""
    return db.query(Lesson).filter(Lesson.difficulty_level == difficulty_level).offset(skip).limit(limit).all()


def count_lessons(db: Session, category: Optional[str] = None) -> int:
    """Count total lessons with optional filtering"""
    query = db.query(Lesson)

    if category:
        query = query.filter(Lesson.category.ilike(f"%{category}%"))

    return query.count()


def complete_lesson_for_user(db: Session, user_id: int, lesson_id: int) -> dict:
    """
    Mark a lesson as completed for a user and update their statistics
    Returns completion details
    """
    # Get the lesson
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        return {"success": False, "message": "Lesson not found"}

    # Get the user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "message": "User not found"}

    # Award points based on lesson score (default to 10 if no score set)
    lesson_score = lesson.lesson_score if lesson.lesson_score is not None else 10

    # Update user statistics
    user.lessons_completed += 1
    user.total_lesson_score += lesson_score

    db.commit()
    db.refresh(user)

    return {
        "success": True,
        "lesson_title": lesson.title,
        "points_earned": lesson_score,
        "total_lessons_completed": user.lessons_completed,
        "total_score": user.total_lesson_score,
        "message": f"Successfully completed '{lesson.title}' and earned {lesson_score} points!"
    }
