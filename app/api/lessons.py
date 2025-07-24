from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependencies import get_db
from app.crud import lesson as lesson_crud
from app.schemas.lesson import LessonCreate, LessonUpdate, LessonResponse, LessonListResponse

router = APIRouter()


@router.post("/", response_model=LessonResponse)
def create_lesson(
    lesson: LessonCreate,
    db: Session = Depends(get_db)
):
    """Create a new lesson"""
    # Check if lesson with same title already exists
    existing_lesson = lesson_crud.get_lesson_by_title(db, lesson.title)
    if existing_lesson:
        raise HTTPException(
            status_code=400, detail="Lesson with this title already exists")

    return lesson_crud.create_lesson(db=db, lesson=lesson)


@router.get("/", response_model=List[LessonListResponse])
def read_lessons(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),
    difficulty_level: Optional[str] = Query(None),
    is_published: Optional[bool] = Query(None),
    instructor_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get lessons with optional filtering"""
    lessons = lesson_crud.get_lessons(
        db=db,
        skip=skip,
        limit=limit,
        category=category,
        difficulty_level=difficulty_level,
        is_published=is_published,
        instructor_id=instructor_id
    )
    return lessons


@router.get("/published", response_model=List[LessonListResponse])
def read_published_lessons(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get only published lessons"""
    lessons = lesson_crud.get_published_lessons(db=db, skip=skip, limit=limit)
    return lessons


@router.get("/search", response_model=List[LessonListResponse])
def search_lessons(
    q: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Search lessons by title, description, or summary"""
    lessons = lesson_crud.search_lessons(
        db=db, search_term=q, skip=skip, limit=limit)
    return lessons


@router.get("/category/{category}", response_model=List[LessonListResponse])
def read_lessons_by_category(
    category: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get lessons by category"""
    lessons = lesson_crud.get_lessons_by_category(
        db=db, category=category, skip=skip, limit=limit)
    return lessons


@router.get("/instructor/{instructor_id}", response_model=List[LessonListResponse])
def read_lessons_by_instructor(
    instructor_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get lessons by instructor"""
    lessons = lesson_crud.get_lessons_by_instructor(
        db=db, instructor_id=instructor_id, skip=skip, limit=limit)
    return lessons


@router.get("/count")
def count_lessons(
    category: Optional[str] = Query(None),
    is_published: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Count total lessons with optional filtering"""
    count = lesson_crud.count_lessons(
        db=db, category=category, is_published=is_published)
    return {"count": count}


@router.get("/{lesson_id}", response_model=LessonResponse)
def read_lesson(lesson_id: int, db: Session = Depends(get_db)):
    """Get a specific lesson by ID"""
    lesson = lesson_crud.get_lesson(db=db, lesson_id=lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson


@router.put("/{lesson_id}", response_model=LessonResponse)
def update_lesson(
    lesson_id: int,
    lesson_update: LessonUpdate,
    db: Session = Depends(get_db)
):
    """Update a lesson"""
    lesson = lesson_crud.update_lesson(
        db=db, lesson_id=lesson_id, lesson_update=lesson_update)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson


@router.patch("/{lesson_id}/publish", response_model=LessonResponse)
def publish_lesson(lesson_id: int, db: Session = Depends(get_db)):
    """Publish a lesson"""
    lesson = lesson_crud.publish_lesson(db=db, lesson_id=lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson


@router.patch("/{lesson_id}/unpublish", response_model=LessonResponse)
def unpublish_lesson(lesson_id: int, db: Session = Depends(get_db)):
    """Unpublish a lesson"""
    lesson = lesson_crud.unpublish_lesson(db=db, lesson_id=lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson


@router.delete("/{lesson_id}")
def delete_lesson(lesson_id: int, db: Session = Depends(get_db)):
    """Delete a lesson"""
    lesson = lesson_crud.delete_lesson(db=db, lesson_id=lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return {"message": "Lesson deleted successfully"}
