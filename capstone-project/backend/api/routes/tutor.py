"""
Tutoring API Routes
===================

Week 1: REST API endpoints for tutoring
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from api.models.schemas import (
    TutoringRequest,
    TutoringResponse,
    VoiceTranscriptionRequest,
    VoiceTranscriptionResponse
)
from agents.tutor_agent import tutoring_system
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/chat", response_model=TutoringResponse)
async def tutor_chat(request: TutoringRequest):
    """
    Main tutoring endpoint - student asks question, agent responds
    
    Integrates Week 6 (multi-agent system) with educational prompting
    """
    
    logger.info(f"Tutoring request: session={request.session_id}, difficulty={request.difficulty}")
    
    try:
        # Call the tutoring agent system
        result = await tutoring_system.tutor_student(
            message=request.message,
            session_id=request.session_id,
            difficulty=request.difficulty.value,
            context=request.context
        )
        
        # Extract suggestions and examples from response (simplified)
        response_text = result["response"]
        
        # Parse for code blocks
        code_examples = []
        if "```python" in response_text:
            # Extract code blocks
            parts = response_text.split("```python")
            for part in parts[1:]:
                code = part.split("```")[0].strip()
                code_examples.append(code)
        
        return TutoringResponse(
            message=response_text,
            session_id=request.session_id,
            suggestions=["Try the example", "Practice with variations", "Ask follow-up questions"],
            related_concepts=["Related topic 1", "Related topic 2"],
            code_examples=code_examples
        )
    
    except Exception as e:
        logger.error(f"Tutoring error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transcribe", response_model=VoiceTranscriptionResponse)
async def transcribe_voice(request: VoiceTranscriptionRequest):
    """
    Week 5: Transcribe voice input to text
    
    In production, would integrate OpenAI Whisper
    """
    
    logger.info(f"Transcription request: session={request.session_id}")
    
    # Mock implementation - in production use Whisper API
    return VoiceTranscriptionResponse(
        text="This would be the transcribed text from audio",
        confidence=0.95,
        language="en"
    )

@router.get("/session/{session_id}/history")
async def get_session_history(session_id: str):
    """
    Retrieve conversation history for a session
    
    Would integrate with database/checkpoint system
    """
    
    logger.info(f"History request: session={session_id}")
    
    # Mock implementation
    return {
        "session_id": session_id,
        "messages": [],
        "started_at": datetime.utcnow().isoformat(),
        "message_count": 0
    }

@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear a tutoring session"""
    
    logger.info(f"Clearing session: {session_id}")
    
    return {
        "status": "cleared",
        "session_id": session_id
    }
