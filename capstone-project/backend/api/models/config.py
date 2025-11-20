"""
Configuration and Settings
===========================

Week 1: Environment variable management and configuration
"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # API Configuration
    API_TOKEN: str = "dev-token-change-in-production"
    REQUIRE_AUTH: bool = False
    ALLOWED_ORIGINS: List[str] = ["http://localhost:8501", "http://localhost:3000"]
    ENVIRONMENT: str = "development"
    
    # OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_TEMPERATURE: float = 0.7
    
    # ElevenLabs (Optional - for voice)
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = ""
    
    # RAG Configuration
    VECTOR_STORE_PATH: str = "./knowledge_base/embeddings"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    MAX_RETRIEVAL_RESULTS: int = 5
    
    # Code Execution
    CODE_TIMEOUT_SECONDS: int = 5
    MAX_CODE_LENGTH: int = 10000
    ALLOWED_IMPORTS: List[str] = [
        "math", "random", "datetime", "json", "re",
        "collections", "itertools", "functools"
    ]
    
    # Agent Configuration
    MAX_AGENT_ITERATIONS: int = 10
    AGENT_TEMPERATURE: float = 0.7
    
    # Database (if using)
    DATABASE_URL: str = "sqlite:///./learning_platform.db"
    
    class Config:
        env_file = "../.env"  # Look in parent directory
        case_sensitive = True

settings = Settings()
