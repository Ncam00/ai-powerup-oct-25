"""
Todo data models using Pydantic for validation and serialization
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict


class TodoBase(BaseModel):
    """Base model with common fields"""
    title: str = Field(..., min_length=1, max_length=200, description="Todo title")
    description: Optional[str] = Field(None, max_length=1000, description="Optional description")
    completed: bool = Field(default=False, description="Completion status")


class TodoCreate(TodoBase):
    """Model for creating a new todo (excludes auto-generated fields)"""
    pass


class TodoUpdate(BaseModel):
    """Model for updating an existing todo (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None


class Todo(TodoBase):
    """Complete todo model with all fields including auto-generated ones"""
    id: UUID = Field(default_factory=uuid4, description="Unique identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: str
        }
    )


class TodoResponse(Todo):
    """Model for API responses"""
    pass


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    status_code: int = Field(..., description="HTTP status code")


class TodoListResponse(BaseModel):
    """Response model for listing todos"""
    todos: list[Todo] = Field(..., description="List of todos")
    total: int = Field(..., description="Total number of todos")
    filtered: bool = Field(default=False, description="Whether results are filtered")