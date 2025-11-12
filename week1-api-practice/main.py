"""
Todo API - Week 1 Agentic Coding Practice
A simple REST API for managing todo items using FastAPI
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from uuid import UUID
from typing import List, Optional

from models.todo import Todo, TodoCreate, TodoUpdate, TodoResponse, TodoListResponse, ErrorResponse
from storage.todo_storage import TodoStorage

# Create FastAPI application
app = FastAPI(
    title="Todo API",
    description="A simple REST API for managing todo items - Week 1 practice project",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize storage
storage = TodoStorage()

# Global exception handler for consistent error responses
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return HTTPException(status_code=400, detail=str(exc))

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return HTTPException(status_code=500, detail="Internal server error")

@app.get("/")
async def root():
    """Root endpoint - API status check"""
    return {
        "message": "Todo API is running!",
        "docs": "/docs",
        "version": "1.0.0",
        "endpoints": {
            "create_todo": "POST /api/todos",
            "list_todos": "GET /api/todos",
            "get_todo": "GET /api/todos/{id}",
            "update_todo": "PUT /api/todos/{id}",
            "toggle_complete": "PATCH /api/todos/{id}/complete",
            "delete_todo": "DELETE /api/todos/{id}"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    stats = storage.count_todos()
    return {
        "status": "healthy",
        "storage": "connected",
        "stats": stats
    }

# API Endpoints

@app.post("/api/todos", response_model=TodoResponse, status_code=201)
async def create_todo(todo_data: TodoCreate):
    """Create a new todo item"""
    try:
        new_todo = storage.create_todo(todo_data)
        return new_todo
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create todo")

@app.get("/api/todos", response_model=TodoListResponse)
async def list_todos(completed: Optional[bool] = Query(None, description="Filter by completion status")):
    """Get all todos, optionally filtered by completion status"""
    try:
        todos = storage.get_all_todos(completed=completed)
        return TodoListResponse(
            todos=todos,
            total=len(todos),
            filtered=completed is not None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve todos")

@app.get("/api/todos/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: UUID):
    """Get a specific todo by ID"""
    try:
        todo = storage.get_todo_by_id(todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
        return todo
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid todo ID format")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve todo")

@app.put("/api/todos/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: UUID, todo_update: TodoUpdate):
    """Update an existing todo"""
    try:
        updated_todo = storage.update_todo(todo_id, todo_update)
        if not updated_todo:
            raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
        return updated_todo
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update todo")

@app.patch("/api/todos/{todo_id}/complete", response_model=TodoResponse)
async def toggle_todo_complete(todo_id: UUID):
    """Toggle the completion status of a todo"""
    try:
        updated_todo = storage.toggle_completed(todo_id)
        if not updated_todo:
            raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
        return updated_todo
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid todo ID format")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to toggle todo completion")

@app.delete("/api/todos/{todo_id}", status_code=204)
async def delete_todo(todo_id: UUID):
    """Delete a todo by ID"""
    try:
        deleted = storage.delete_todo(todo_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
        return  # 204 No Content
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid todo ID format")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to delete todo")

@app.get("/api/stats")
async def get_stats():
    """Get todo statistics"""
    try:
        stats = storage.count_todos()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get statistics")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)