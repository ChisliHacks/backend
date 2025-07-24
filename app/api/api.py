from fastapi import APIRouter
from app.api import auth, lessons, jobs, upload, ai_chat

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(lessons.router, prefix="/lessons", tags=["lessons"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(ai_chat.router, tags=["ai"])
