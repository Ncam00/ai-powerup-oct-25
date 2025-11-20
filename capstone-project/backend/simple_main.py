"""
Simplified FastAPI Backend for PythonMentor AI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from openai import OpenAI

# Load environment variables
from dotenv import load_dotenv
load_dotenv("../.env")

app = FastAPI(title="PythonMentor AI API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Models
class TutoringRequest(BaseModel):
    message: str
    session_id: str
    difficulty: str = "beginner"
    use_voice: bool = False
    context: List[dict] = []

class TutoringResponse(BaseModel):
    message: str
    code_examples: List[str] = []
    session_id: str

class CodeExecutionRequest(BaseModel):
    code: str
    session_id: str

class CodeExecutionResponse(BaseModel):
    output: str
    error: Optional[str] = None
    execution_time: float

# Routes
@app.get("/")
async def root():
    return {"message": "PythonMentor AI API is running!", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "api_key_configured": bool(os.getenv("OPENAI_API_KEY"))}

@app.post("/tutor/chat", response_model=TutoringResponse)
async def tutor_chat(request: TutoringRequest):
    """AI Tutoring endpoint"""
    try:
        # Create system prompt based on difficulty
        system_prompts = {
            "beginner": "You are a patient Python tutor for beginners. Explain concepts simply with examples.",
            "intermediate": "You are a Python tutor for intermediate learners. Provide detailed explanations and best practices.",
            "advanced": "You are a Python expert. Discuss advanced concepts, optimizations, and design patterns."
        }
        
        system_prompt = system_prompts.get(request.difficulty, system_prompts["beginner"])
        
        # Call OpenAI
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message}
            ],
            temperature=0.7
        )
        
        message = response.choices[0].message.content
        
        # Extract code examples (simple heuristic)
        code_examples = []
        if "```python" in message:
            parts = message.split("```python")
            for part in parts[1:]:
                if "```" in part:
                    code = part.split("```")[0].strip()
                    code_examples.append(code)
        
        return TutoringResponse(
            message=message,
            code_examples=code_examples,
            session_id=request.session_id
        )
    
    except Exception as e:
        return TutoringResponse(
            message=f"Sorry, I encountered an error: {str(e)}",
            code_examples=[],
            session_id=request.session_id
        )

@app.post("/code/execute", response_model=CodeExecutionResponse)
async def execute_code(request: CodeExecutionRequest):
    """Execute Python code safely"""
    import time
    import io
    import sys
    from contextlib import redirect_stdout, redirect_stderr
    
    start_time = time.time()
    
    try:
        # Capture output
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            # Create restricted globals
            safe_globals = {
                "__builtins__": {
                    "print": print,
                    "len": len,
                    "range": range,
                    "str": str,
                    "int": int,
                    "float": float,
                    "list": list,
                    "dict": dict,
                    "tuple": tuple,
                    "set": set,
                    "sum": sum,
                    "max": max,
                    "min": min,
                    "abs": abs,
                    "round": round,
                    "enumerate": enumerate,
                    "zip": zip,
                    "map": map,
                    "filter": filter,
                }
            }
            
            # Execute code
            exec(request.code, safe_globals)
        
        execution_time = time.time() - start_time
        output = stdout_capture.getvalue()
        error = stderr_capture.getvalue()
        
        return CodeExecutionResponse(
            output=output if output else "Code executed successfully (no output)",
            error=error if error else None,
            execution_time=execution_time
        )
    
    except Exception as e:
        execution_time = time.time() - start_time
        return CodeExecutionResponse(
            output="",
            error=str(e),
            execution_time=execution_time
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
