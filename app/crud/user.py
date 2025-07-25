from sqlalchemy.orm import Session
from app.models.user import User
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
