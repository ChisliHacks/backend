from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    message: str
    conversation_history: List[ChatMessage] = []


class ChatResponse(BaseModel):
    response: str
    conversation_id: Optional[str] = None


class SummarizeRequest(BaseModel):
    text: str
    summary_type: str = "general"  # "general", "key_points", "brief"


class SummarizeResponse(BaseModel):
    summary: str
    original_length: int
    summary_length: int


class LessonSummaryRequest(BaseModel):
    lesson_id: int
    summary_type: str = "general"


class LessonSummaryResponse(BaseModel):
    lesson_id: int
    lesson_title: str
    summary: str
    key_points: List[str] = []


class JobSuggestionRequest(BaseModel):
    lesson_title: str
    lesson_description: str
    lesson_category: str


class JobSuggestionResponse(BaseModel):
    suggested_job_positions: List[str]
    reasoning: str = ""
