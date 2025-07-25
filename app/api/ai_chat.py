from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging

from app.schemas.ai_chat import (
    ChatRequest, ChatResponse,
    SummarizeRequest, SummarizeResponse,
    LessonSummaryRequest, LessonSummaryResponse,
    JobSuggestionRequest, JobSuggestionResponse
)
from app.core.ai_service import tuna_ai
from app.core.dependencies import get_current_user
from app.crud.lesson import get_lesson
from app.core.database import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Assistant - Tuna"])


@router.post("/chat", response_model=ChatResponse)
async def chat_with_tuna(
    request: ChatRequest,
    current_user=Depends(get_current_user)
):
    """
    Chat with Tuna AI assistant
    """
    try:
        response = await tuna_ai.chat(
            message=request.message,
            conversation_history=request.conversation_history
        )

        return ChatResponse(response=response)

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to process chat request")


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_text(
    request: SummarizeRequest,
    current_user=Depends(get_current_user)
):
    """
    Summarize any text content
    """
    try:
        result = await tuna_ai.summarize_text(
            text=request.text,
            summary_type=request.summary_type
        )

        return SummarizeResponse(
            summary=result["summary"],
            original_length=result["original_length"],
            summary_length=result["summary_length"]
        )

    except Exception as e:
        logger.error(f"Error in summarize endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to summarize text")


@router.post("/summarize-lesson", response_model=LessonSummaryResponse)
async def summarize_lesson(
    request: LessonSummaryRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Summarize a specific lesson by ID
    """
    try:
        # Get lesson from database
        lesson = get_lesson(db, request.lesson_id)
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")

        # Prepare lesson content for summarization
        lesson_content = f"""
        Title: {lesson.title}
        Category: {lesson.category}
        Difficulty: {lesson.difficulty_level}
        Description: {lesson.description or 'No description available'}
        Duration: {lesson.duration_minutes or 'Not specified'} minutes
        
        [Note: This lesson may have associated files that are not included in this summary]
        """

        # Get summary from AI
        result = await tuna_ai.summarize_lesson(
            lesson_content=lesson_content,
            lesson_title=lesson.title
        )

        return LessonSummaryResponse(
            lesson_id=lesson.id,
            lesson_title=lesson.title,
            summary=result["summary"],
            key_points=result["key_points"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in lesson summarization endpoint: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to summarize lesson")


@router.post("/suggest-jobs", response_model=JobSuggestionResponse)
async def suggest_related_jobs(
    request: JobSuggestionRequest,
    current_user=Depends(get_current_user)
):
    """
    Suggest related job positions for a lesson based on its content
    """
    try:
        # Get AI suggestions (now returns job position strings)
        suggested_positions = await tuna_ai.suggest_related_jobs(
            lesson_title=request.lesson_title,
            lesson_description=request.lesson_description,
            lesson_category=request.lesson_category
        )

        return JobSuggestionResponse(
            suggested_job_positions=suggested_positions,
            reasoning="Job positions suggested based on lesson content analysis"
        )

    except Exception as e:
        logger.error(f"Error in job suggestion endpoint: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to suggest related jobs")


@router.get("/status")
async def get_ai_status(current_user=Depends(get_current_user)):
    """
    Check AI service status and model availability
    """
    try:
        model_available = tuna_ai.check_model_availability()

        return {
            "status": "online" if model_available else "model_not_available",
            "model": tuna_ai.model_name,
            "model_available": model_available,
            "message": "Tuna is ready to help!" if model_available else "Model needs to be downloaded"
        }

    except Exception as e:
        logger.error(f"Error checking AI status: {str(e)}")
        return {
            "status": "offline",
            "model": tuna_ai.model_name,
            "model_available": False,
            "message": "AI service is currently unavailable"
        }


@router.post("/setup-model")
async def setup_model(current_user=Depends(get_current_user)):
    """
    Download and setup the AI model (admin only)
    """
    try:
        # Check if model is already available
        if tuna_ai.check_model_availability():
            return {
                "status": "success",
                "message": f"Model {tuna_ai.model_name} is already available"
            }

        # Pull the model
        success = await tuna_ai.pull_model()

        if success:
            return {
                "status": "success",
                "message": f"Model {tuna_ai.model_name} has been downloaded successfully"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to download model. Please check Ollama installation."
            )

    except Exception as e:
        logger.error(f"Error setting up model: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to setup AI model")
