"""
Main FastAPI Application
========================

Integrates Week 1 (API Fundamentals) with all advanced features.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from api.routes import tutor, code, quiz, progress
from api.models.config import Settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
settings = Settings()

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting AI Code Learning Platform API")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info("Initializing RAG system...")
    # Initialize vector store, load models, etc.
    
    yield
    
    # Shutdown
    logger.info("Shutting down API...")

# Create FastAPI app
app = FastAPI(
    title="AI Code Learning Platform API",
    description="Capstone project integrating Weeks 1-6 AI techniques",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token (simplified for demo)"""
    token = credentials.credentials
    # In production: verify JWT signature, expiration, etc.
    if token != settings.API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return token

# Include routers
app.include_router(
    tutor.router,
    prefix="/api/v1/tutor",
    tags=["Tutoring"],
    dependencies=[Depends(verify_token)] if settings.REQUIRE_AUTH else []
)

app.include_router(
    code.router,
    prefix="/api/v1/code",
    tags=["Code Execution"],
    dependencies=[Depends(verify_token)] if settings.REQUIRE_AUTH else []
)

app.include_router(
    quiz.router,
    prefix="/api/v1/quiz",
    tags=["Quizzes & Assessments"],
    dependencies=[Depends(verify_token)] if settings.REQUIRE_AUTH else []
)

app.include_router(
    progress.router,
    prefix="/api/v1/progress",
    tags=["Learning Progress"],
    dependencies=[Depends(verify_token)] if settings.REQUIRE_AUTH else []
)

# Root endpoints
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "AI Code Learning Platform API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs",
        "features": {
            "tutoring": "Multi-agent AI tutoring system",
            "code_execution": "Safe Python code sandbox",
            "rag": "Python documentation retrieval",
            "voice": "Speech-to-text and text-to-speech",
            "quizzes": "Adaptive assessment generation",
            "progress": "Learning analytics and tracking"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "operational",
            "database": "operational",  # Check actual DB connection
            "llm": "operational",        # Check OpenAI API
            "vector_store": "operational" # Check ChromaDB
        }
    }

@app.get("/api/v1/stats")
async def api_stats():
    """API usage statistics"""
    return {
        "total_tutoring_sessions": 0,  # From database
        "code_executions": 0,
        "quizzes_generated": 0,
        "active_learners": 0,
        "uptime_hours": 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
