"""
Code Execution API Routes
==========================

Week 3: Tool use endpoints
"""

from fastapi import APIRouter, HTTPException
from api.models.schemas import (
    CodeExecutionRequest,
    CodeExecutionResponse,
    CodeReviewRequest,
    CodeReviewResponse
)
from tools.code_executor import execute_python_code
from tools.code_analyzer import analyze_code_quality, get_code_metrics
import logging
import time

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/execute", response_model=CodeExecutionResponse)
async def execute_code(request: CodeExecutionRequest):
    """
    Execute Python code safely
    
    Week 3: Demonstrates tool use for code execution
    """
    
    logger.info(f"Code execution request: session={request.session_id}")
    
    start_time = time.time()
    
    try:
        # Execute code using tool
        result = execute_python_code.invoke({"code": request.code})
        
        execution_time = time.time() - start_time
        
        # Determine success based on result
        success = not result.startswith("❌")
        
        return CodeExecutionResponse(
            success=success,
            output=result if success else None,
            error=result if not success else None,
            execution_time=execution_time,
            warnings=[]
        )
    
    except Exception as e:
        logger.error(f"Execution error: {e}")
        return CodeExecutionResponse(
            success=False,
            error=str(e),
            execution_time=time.time() - start_time,
            warnings=[]
        )

@router.post("/review", response_model=CodeReviewResponse)
async def review_code(request: CodeReviewRequest):
    """
    Analyze code quality and provide feedback
    
    Week 3: Structured output from code analysis
    """
    
    logger.info(f"Code review request: {len(request.code)} chars")
    
    try:
        # Get analysis from tool
        analysis = analyze_code_quality.invoke({"code": request.code})
        
        # Get metrics
        metrics = get_code_metrics(request.code)
        
        # Parse analysis for structured response
        # (Simplified - in production would use LLM with structured output)
        
        return CodeReviewResponse(
            overall_score=75,  # Would parse from analysis
            issues=[
                {"line": 1, "severity": "warning", "message": "Example issue"},
            ],
            suggestions=[
                "Use more descriptive variable names",
                "Add docstrings to functions"
            ],
            good_practices=[
                "Good use of list comprehensions",
                "Proper error handling"
            ],
            complexity_score=metrics.get("complexity", 1),
            summary=analysis
        )
    
    except Exception as e:
        logger.error(f"Review error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/examples/{topic}")
async def get_code_examples(topic: str, difficulty: str = "beginner"):
    """
    Get code examples for a topic
    
    Uses RAG (Week 4) to find relevant examples
    """
    
    logger.info(f"Examples request: topic={topic}, difficulty={difficulty}")
    
    # Mock examples - in production would use RAG retrieval
    examples = {
        "lists": [
            "# Create a list\nmy_list = [1, 2, 3, 4, 5]",
            "# List comprehension\nsquares = [x**2 for x in range(10)]"
        ],
        "functions": [
            "def greet(name):\n    return f'Hello, {name}!'",
            "def add(a, b):\n    \"\"\"Add two numbers\"\"\"\n    return a + b"
        ]
    }
    
    return {
        "topic": topic,
        "difficulty": difficulty,
        "examples": examples.get(topic, ["No examples found"])
    }
