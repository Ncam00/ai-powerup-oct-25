"""
Test configuration and fixtures for the Todo API
"""

import pytest
import tempfile
import os
from pathlib import Path
from fastapi.testclient import TestClient
from uuid import uuid4

from main import app
from storage.todo_storage import TodoStorage
from models.todo import TodoCreate

# Override the storage to use temporary file for testing
original_storage = None

@pytest.fixture(autouse=True)
def setup_test_storage():
    """Automatically use temporary storage for all tests"""
    global original_storage
    from main import storage
    
    # Save original storage
    original_storage = storage
    
    # Create temporary storage for test
    with tempfile.TemporaryDirectory() as temp_dir:
        test_storage_file = Path(temp_dir) / "test_todos.json"
        test_storage = TodoStorage(str(test_storage_file))
        
        # Replace the storage in main module
        import main
        main.storage = test_storage
        
        yield test_storage
        
        # Restore original storage
        main.storage = original_storage


@pytest.fixture
def client():
    """Create a test client for the FastAPI application"""
    return TestClient(app)


@pytest.fixture
def temp_storage():
    """Create a temporary storage for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_file = Path(temp_dir) / "test_todos.json"
        storage = TodoStorage(str(storage_file))
        yield storage


@pytest.fixture
def sample_todo_data():
    """Sample todo data for testing"""
    return {
        "title": "Test Todo",
        "description": "This is a test todo item",
        "completed": False
    }


@pytest.fixture
def sample_todos():
    """Multiple sample todos for testing"""
    return [
        {"title": "First Todo", "description": "First test item", "completed": False},
        {"title": "Second Todo", "description": "Second test item", "completed": True},
        {"title": "Third Todo", "description": "Third test item", "completed": False},
    ]


@pytest.fixture
def populated_storage(temp_storage, sample_todos):
    """Storage populated with sample data"""
    created_todos = []
    for todo_data in sample_todos:
        todo_create = TodoCreate(**todo_data)
        created_todo = temp_storage.create_todo(todo_create)
        created_todos.append(created_todo)
    
    return temp_storage, created_todos


@pytest.fixture
def invalid_uuid():
    """Invalid UUID for testing error cases"""
    return "invalid-uuid-string"


@pytest.fixture
def non_existent_uuid():
    """Valid UUID that doesn't exist in storage"""
    return str(uuid4())