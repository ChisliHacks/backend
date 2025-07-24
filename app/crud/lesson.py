from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.lesson import Lesson
from app.schemas.lesson import LessonCreate, LessonUpdate


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
    difficulty_level: Optional[str] = None,
    is_published: Optional[bool] = None,
    instructor_id: Optional[int] = None
) -> List[Lesson]:
    """Get multiple lessons with optional filtering"""
    query = db.query(Lesson)

    if category:
        query = query.filter(Lesson.category == category)

    if difficulty_level:
        query = query.filter(Lesson.difficulty_level == difficulty_level)

    if is_published is not None:
        query = query.filter(Lesson.is_published == is_published)

    if instructor_id:
        query = query.filter(Lesson.instructor_id == instructor_id)

    return query.offset(skip).limit(limit).all()


def get_published_lessons(db: Session, skip: int = 0, limit: int = 100) -> List[Lesson]:
    """Get only published lessons"""
    return db.query(Lesson).filter(Lesson.is_published == True).offset(skip).limit(limit).all()


def get_lessons_by_category(db: Session, category: str, skip: int = 0, limit: int = 100) -> List[Lesson]:
    """Get lessons by category"""
    return db.query(Lesson).filter(Lesson.category == category).offset(skip).limit(limit).all()


def get_lessons_by_instructor(db: Session, instructor_id: int, skip: int = 0, limit: int = 100) -> List[Lesson]:
    """Get lessons by instructor"""
    return db.query(Lesson).filter(Lesson.instructor_id == instructor_id).offset(skip).limit(limit).all()


def create_lesson(db: Session, lesson: LessonCreate) -> Lesson:
    """Create a new lesson"""
    db_lesson = Lesson(
        title=lesson.title,
        description=lesson.description,
        category=lesson.category,
        filename=lesson.filename,
        duration_minutes=lesson.duration_minutes,
        difficulty_level=lesson.difficulty_level,
        is_published=lesson.is_published,
        instructor_id=lesson.instructor_id
    )
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)
    return db_lesson


def update_lesson(db: Session, lesson_id: int, lesson_update: LessonUpdate) -> Optional[Lesson]:
    """Update an existing lesson"""
    db_lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if db_lesson:
        update_data = lesson_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_lesson, field, value)
        db.commit()
        db.refresh(db_lesson)
    return db_lesson


def delete_lesson(db: Session, lesson_id: int) -> Optional[Lesson]:
    """Delete a lesson"""
    db_lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if db_lesson:
        db.delete(db_lesson)
        db.commit()
    return db_lesson


def publish_lesson(db: Session, lesson_id: int) -> Optional[Lesson]:
    """Publish a lesson (set is_published to True)"""
    db_lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if db_lesson:
        db_lesson.is_published = True
        db.commit()
        db.refresh(db_lesson)
    return db_lesson


def unpublish_lesson(db: Session, lesson_id: int) -> Optional[Lesson]:
    """Unpublish a lesson (set is_published to False)"""
    db_lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if db_lesson:
        db_lesson.is_published = False
        db.commit()
        db.refresh(db_lesson)
    return db_lesson


def search_lessons(db: Session, search_term: str, skip: int = 0, limit: int = 100) -> List[Lesson]:
    """Search lessons by title or description"""
    return db.query(Lesson).filter(
        Lesson.title.contains(search_term) |
        Lesson.description.contains(search_term)
    ).offset(skip).limit(limit).all()


def count_lessons(db: Session, category: Optional[str] = None, is_published: Optional[bool] = None) -> int:
    """Count total lessons with optional filtering"""
    query = db.query(Lesson)

    if category:
        query = query.filter(Lesson.category == category)

    if is_published is not None:
        query = query.filter(Lesson.is_published == is_published)

    return query.count()
