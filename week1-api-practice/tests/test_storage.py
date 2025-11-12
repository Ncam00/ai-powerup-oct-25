"""
Unit tests for TodoStorage class
"""

import pytest
from uuid import UUID
from models.todo import TodoCreate, TodoUpdate
from storage.todo_storage import TodoStorage


class TestTodoStorage:
    """Test cases for TodoStorage functionality"""
    
    def test_storage_initialization(self, temp_storage):
        """Test storage initializes correctly"""
        assert isinstance(temp_storage, TodoStorage)
        assert temp_storage.storage_file.exists()
        
    def test_create_todo(self, temp_storage, sample_todo_data):
        """Test creating a new todo"""
        todo_create = TodoCreate(**sample_todo_data)
        created_todo = temp_storage.create_todo(todo_create)
        
        assert created_todo.title == sample_todo_data["title"]
        assert created_todo.description == sample_todo_data["description"]
        assert created_todo.completed == sample_todo_data["completed"]
        assert isinstance(created_todo.id, UUID)
        assert created_todo.created_at is not None
        assert created_todo.updated_at is not None
        
    def test_get_all_todos_empty(self, temp_storage):
        """Test getting todos from empty storage"""
        todos = temp_storage.get_all_todos()
        assert todos == []
        
    def test_get_all_todos_populated(self, populated_storage):
        """Test getting all todos from populated storage"""
        storage, created_todos = populated_storage
        todos = storage.get_all_todos()
        
        assert len(todos) == 3
        assert todos[0].title == "First Todo"
        assert todos[1].title == "Second Todo"
        assert todos[2].title == "Third Todo"
        
    def test_get_todos_filtered_by_completed(self, populated_storage):
        """Test filtering todos by completion status"""
        storage, created_todos = populated_storage
        
        # Get only completed todos
        completed_todos = storage.get_all_todos(completed=True)
        assert len(completed_todos) == 1
        assert completed_todos[0].title == "Second Todo"
        
        # Get only pending todos
        pending_todos = storage.get_all_todos(completed=False)
        assert len(pending_todos) == 2
        assert pending_todos[0].title == "First Todo"
        assert pending_todos[1].title == "Third Todo"
        
    def test_get_todo_by_id_existing(self, populated_storage):
        """Test getting an existing todo by ID"""
        storage, created_todos = populated_storage
        first_todo = created_todos[0]
        
        retrieved_todo = storage.get_todo_by_id(first_todo.id)
        assert retrieved_todo is not None
        assert retrieved_todo.id == first_todo.id
        assert retrieved_todo.title == first_todo.title
        
    def test_get_todo_by_id_non_existent(self, temp_storage, non_existent_uuid):
        """Test getting a non-existent todo by ID"""
        retrieved_todo = temp_storage.get_todo_by_id(UUID(non_existent_uuid))
        assert retrieved_todo is None
        
    def test_update_todo_existing(self, populated_storage):
        """Test updating an existing todo"""
        storage, created_todos = populated_storage
        first_todo = created_todos[0]
        
        update_data = TodoUpdate(
            title="Updated Title",
            description="Updated description",
            completed=True
        )
        
        updated_todo = storage.update_todo(first_todo.id, update_data)
        assert updated_todo is not None
        assert updated_todo.title == "Updated Title"
        assert updated_todo.description == "Updated description"
        assert updated_todo.completed == True
        assert updated_todo.updated_at > first_todo.updated_at
        
    def test_update_todo_partial(self, populated_storage):
        """Test partial update of a todo"""
        storage, created_todos = populated_storage
        first_todo = created_todos[0]
        original_description = first_todo.description
        
        update_data = TodoUpdate(title="Only Title Changed")
        
        updated_todo = storage.update_todo(first_todo.id, update_data)
        assert updated_todo is not None
        assert updated_todo.title == "Only Title Changed"
        assert updated_todo.description == original_description  # Unchanged
        assert updated_todo.completed == first_todo.completed  # Unchanged
        
    def test_update_todo_non_existent(self, temp_storage, non_existent_uuid):
        """Test updating a non-existent todo"""
        update_data = TodoUpdate(title="Should not work")
        updated_todo = temp_storage.update_todo(UUID(non_existent_uuid), update_data)
        assert updated_todo is None
        
    def test_delete_todo_existing(self, populated_storage):
        """Test deleting an existing todo"""
        storage, created_todos = populated_storage
        first_todo = created_todos[0]
        
        # Verify todo exists before deletion
        assert storage.get_todo_by_id(first_todo.id) is not None
        
        # Delete todo
        deleted = storage.delete_todo(first_todo.id)
        assert deleted == True
        
        # Verify todo no longer exists
        assert storage.get_todo_by_id(first_todo.id) is None
        
        # Verify other todos still exist
        remaining_todos = storage.get_all_todos()
        assert len(remaining_todos) == 2
        
    def test_delete_todo_non_existent(self, temp_storage, non_existent_uuid):
        """Test deleting a non-existent todo"""
        deleted = temp_storage.delete_todo(UUID(non_existent_uuid))
        assert deleted == False
        
    def test_toggle_completed_existing(self, populated_storage):
        """Test toggling completion status of existing todo"""
        storage, created_todos = populated_storage
        first_todo = created_todos[0]  # Initially not completed
        
        # Toggle to completed
        toggled_todo = storage.toggle_completed(first_todo.id)
        assert toggled_todo is not None
        assert toggled_todo.completed == True
        assert toggled_todo.updated_at > first_todo.updated_at
        
        # Toggle back to not completed
        toggled_again = storage.toggle_completed(first_todo.id)
        assert toggled_again is not None
        assert toggled_again.completed == False
        
    def test_toggle_completed_non_existent(self, temp_storage, non_existent_uuid):
        """Test toggling completion of non-existent todo"""
        toggled_todo = temp_storage.toggle_completed(UUID(non_existent_uuid))
        assert toggled_todo is None
        
    def test_count_todos_empty(self, temp_storage):
        """Test counting todos in empty storage"""
        stats = temp_storage.count_todos()
        assert stats == {"total": 0, "completed": 0, "pending": 0}
        
    def test_count_todos_populated(self, populated_storage):
        """Test counting todos in populated storage"""
        storage, created_todos = populated_storage
        stats = storage.count_todos()
        
        assert stats["total"] == 3
        assert stats["completed"] == 1  # Second todo is completed
        assert stats["pending"] == 2
        
    def test_storage_persistence(self, temp_storage, sample_todo_data):
        """Test that data persists across storage instances"""
        # Create todo with first storage instance
        todo_create = TodoCreate(**sample_todo_data)
        created_todo = temp_storage.create_todo(todo_create)
        
        # Create new storage instance with same file
        new_storage = TodoStorage(str(temp_storage.storage_file))
        todos = new_storage.get_all_todos()
        
        assert len(todos) == 1
        assert todos[0].title == created_todo.title
        assert todos[0].id == created_todo.id