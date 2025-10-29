"""
Learning Progress Models for PythonMentor AI using Pydantic
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

class SkillLevel(str, Enum):
    """Enum for student skill levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate" 
    ADVANCED = "advanced"

class TopicCategory(str, Enum):
    """Categories of Python topics"""
    FUNDAMENTALS = "fundamentals"
    DATA_STRUCTURES = "data_structures"
    CONTROL_FLOW = "control_flow"
    FUNCTIONS = "functions"
    OOP = "object_oriented"
    ERROR_HANDLING = "error_handling"
    LIBRARIES = "libraries"
    BEST_PRACTICES = "best_practices"

class LearningObjective(BaseModel):
    """Individual learning objective with structured tracking"""
    topic: str = Field(..., description="Name of the topic or concept")
    category: TopicCategory = Field(..., description="Category this topic belongs to")
    difficulty: SkillLevel = Field(..., description="Recommended skill level for this topic")
    description: str = Field(..., description="Brief description of what student should learn")
    completed: bool = Field(default=False, description="Whether student has demonstrated understanding")
    confidence_score: Optional[float] = Field(None, description="AI's assessment of student understanding (0-1)")

class ConversationAnalysis(BaseModel):
    """Structured analysis of a tutoring conversation"""
    topics_discussed: List[str] = Field(default_factory=list, description="Topics covered in this conversation")
    student_questions: List[str] = Field(default_factory=list, description="Questions asked by student")
    code_examples_shown: List[str] = Field(default_factory=list, description="Code examples provided")
    learning_objectives_addressed: List[str] = Field(default_factory=list, description="Learning objectives worked on")
    student_understanding_level: Optional[float] = Field(None, description="Estimated understanding level (0-1)")
    suggested_next_topics: List[str] = Field(default_factory=list, description="Recommended topics for next session")
    session_summary: str = Field(..., description="Brief summary of the learning session")

class StudentProgress(BaseModel):
    """Complete student progress tracking"""
    student_id: str = Field(..., description="Unique identifier for student")
    current_level: SkillLevel = Field(..., description="Current assessed skill level")
    learning_objectives: List[LearningObjective] = Field(default_factory=list, description="All learning objectives")
    conversation_history: List[ConversationAnalysis] = Field(default_factory=list, description="Past conversation analyses")
    strengths: List[str] = Field(default_factory=list, description="Student's identified strengths")
    areas_for_improvement: List[str] = Field(default_factory=list, description="Areas needing more work")
    total_sessions: int = Field(default=0, description="Total number of tutoring sessions")
    overall_progress_score: Optional[float] = Field(None, description="Overall progress assessment (0-1)")