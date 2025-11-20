"""
Pydantic Models for API
========================

Week 1: Request/Response validation with Pydantic
Week 3: Structured outputs
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum

# ============================================================================
# TUTORING MODELS
# ============================================================================

class DifficultyLevel(str, Enum):
    """Learning difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class TutoringRequest(BaseModel):
    """Request for tutoring interaction"""
    message: str = Field(..., min_length=1, max_length=5000)
    session_id: str = Field(..., description="Unique session identifier")
    use_voice: bool = Field(default=False, description="Enable voice response")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.BEGINNER)
    context: Optional[List[Dict[str, str]]] = Field(default=None, description="Conversation history")

class TutoringResponse(BaseModel):
    """Response from tutoring agent"""
    message: str
    session_id: str
    audio_url: Optional[str] = None
    suggestions: List[str] = Field(default_factory=list)
    related_concepts: List[str] = Field(default_factory=list)
    code_examples: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# ============================================================================
# CODE EXECUTION MODELS
# ============================================================================

class CodeExecutionRequest(BaseModel):
    """Request to execute Python code"""
    code: str = Field(..., min_length=1, max_length=10000)
    session_id: str
    timeout: int = Field(default=5, ge=1, le=30)
    
    @validator('code')
    def validate_code(cls, v):
        """Basic code validation"""
        if 'import os' in v or 'import sys' in v or '__import__' in v:
            raise ValueError("Restricted imports detected")
        return v

class CodeExecutionResponse(BaseModel):
    """Response from code execution"""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: float
    warnings: List[str] = Field(default_factory=list)

class CodeReviewRequest(BaseModel):
    """Request for code review"""
    code: str = Field(..., min_length=1, max_length=10000)
    focus_areas: List[str] = Field(
        default_factory=lambda: ["style", "bugs", "performance"],
        description="What to focus on: style, bugs, performance, readability"
    )

class CodeReviewResponse(BaseModel):
    """Structured code review response"""
    overall_score: int = Field(..., ge=0, le=100)
    issues: List[Dict[str, Any]] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    good_practices: List[str] = Field(default_factory=list)
    complexity_score: int = Field(..., ge=0, le=10)
    summary: str

# ============================================================================
# QUIZ MODELS
# ============================================================================

class QuizDifficulty(str, Enum):
    """Quiz difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class QuestionType(str, Enum):
    """Types of quiz questions"""
    MULTIPLE_CHOICE = "multiple_choice"
    CODE_COMPLETION = "code_completion"
    DEBUG = "debug"
    EXPLAIN = "explain"

class QuizGenerationRequest(BaseModel):
    """Request to generate a quiz"""
    topic: str = Field(..., description="Python topic to quiz on")
    difficulty: QuizDifficulty = Field(default=QuizDifficulty.MEDIUM)
    num_questions: int = Field(default=5, ge=1, le=20)
    question_types: List[QuestionType] = Field(
        default_factory=lambda: [QuestionType.MULTIPLE_CHOICE]
    )

class QuizQuestion(BaseModel):
    """Individual quiz question"""
    question_id: str
    type: QuestionType
    question: str
    options: Optional[List[str]] = None  # For multiple choice
    code_snippet: Optional[str] = None   # For code-based questions
    correct_answer: str
    explanation: str
    difficulty: QuizDifficulty

class QuizResponse(BaseModel):
    """Generated quiz"""
    quiz_id: str
    topic: str
    difficulty: QuizDifficulty
    questions: List[QuizQuestion]
    estimated_time_minutes: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

class QuizSubmission(BaseModel):
    """Student's quiz submission"""
    quiz_id: str
    session_id: str
    answers: Dict[str, str]  # question_id -> answer
    
class QuizResult(BaseModel):
    """Quiz grading results"""
    quiz_id: str
    session_id: str
    score: int = Field(..., ge=0, le=100)
    correct_answers: int
    total_questions: int
    feedback: List[Dict[str, Any]]
    areas_to_improve: List[str]
    next_recommended_topics: List[str]

# ============================================================================
# PROGRESS TRACKING MODELS
# ============================================================================

class LearningProgress(BaseModel):
    """Student's learning progress"""
    session_id: str
    topics_covered: List[str]
    topics_mastered: List[str]
    current_level: DifficultyLevel
    total_coding_time_minutes: int
    quizzes_completed: int
    average_quiz_score: float = Field(..., ge=0, le=100)
    strengths: List[str]
    weaknesses: List[str]
    recommended_next_steps: List[str]

class ConceptMastery(BaseModel):
    """Mastery level for a specific concept"""
    concept: str
    mastery_level: int = Field(..., ge=0, le=100)
    practice_count: int
    last_practiced: datetime
    needs_review: bool

# ============================================================================
# VOICE MODELS (Week 5)
# ============================================================================

class VoiceTranscriptionRequest(BaseModel):
    """Request to transcribe audio"""
    audio_base64: str = Field(..., description="Base64 encoded audio")
    session_id: str

class VoiceTranscriptionResponse(BaseModel):
    """Transcription result"""
    text: str
    confidence: float = Field(..., ge=0, le=1)
    language: str = "en"

class TTSRequest(BaseModel):
    """Text-to-speech request"""
    text: str = Field(..., min_length=1, max_length=5000)
    voice_id: Optional[str] = None
    session_id: str

class TTSResponse(BaseModel):
    """TTS result"""
    audio_url: str
    duration_seconds: float

# ============================================================================
# RAG MODELS (Week 4)
# ============================================================================

class ConceptSearchRequest(BaseModel):
    """Search Python documentation"""
    query: str = Field(..., min_length=1, max_length=500)
    max_results: int = Field(default=5, ge=1, le=20)
    min_relevance_score: float = Field(default=0.7, ge=0, le=1)

class ConceptSearchResult(BaseModel):
    """Single search result"""
    concept: str
    content: str
    relevance_score: float
    source: str
    examples: List[str] = Field(default_factory=list)

class ConceptSearchResponse(BaseModel):
    """Search results"""
    query: str
    results: List[ConceptSearchResult]
    total_found: int
