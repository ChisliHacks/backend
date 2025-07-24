from fastapi import APIRouter
from app.api import auth, lessons, jobs

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(lessons.router, prefix="/lessons", tags=["lessons"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
