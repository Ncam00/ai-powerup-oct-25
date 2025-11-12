"""
JSON file-based storage for todo items with thread safety
"""

import json
import os
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from models.todo import Todo, TodoCreate, TodoUpdate


class TodoStorage:
    """JSON file-based storage for todo items"""
    
    def __init__(self, storage_file: str = "storage/todos.json"):
        self.storage_file = Path(storage_file)
        self._lock = Lock()
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self):
        """Create storage directory and file if they don't exist"""
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_file.exists():
            self._write_data([])
    
    def _read_data(self) -> List[Dict[str, Any]]:
        """Read data from JSON file with error handling"""
        try:
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _write_data(self, data: List[Dict[str, Any]]):
        """Write data to JSON file with proper formatting"""
        with open(self.storage_file, 'w') as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)
    
    def _dict_to_todo(self, todo_dict: Dict[str, Any]) -> Todo:
        """Convert dictionary to Todo model"""
        # Handle UUID conversion
        if isinstance(todo_dict.get('id'), str):
            todo_dict['id'] = UUID(todo_dict['id'])
        
        # Handle datetime conversion
        for field in ['created_at', 'updated_at']:
            if isinstance(todo_dict.get(field), str):
                todo_dict[field] = datetime.fromisoformat(todo_dict[field].replace('Z', '+00:00'))
        
        return Todo(**todo_dict)
    
    def _todo_to_dict(self, todo: Todo) -> Dict[str, Any]:
        """Convert Todo model to dictionary for JSON storage"""
        return {
            'id': str(todo.id),
            'title': todo.title,
            'description': todo.description,
            'completed': todo.completed,
            'created_at': todo.created_at.isoformat(),
            'updated_at': todo.updated_at.isoformat()
        }
    
    def create_todo(self, todo_data: TodoCreate) -> Todo:
        """Create a new todo item"""
        with self._lock:
            # Create new todo with auto-generated fields
            new_todo = Todo(
                id=uuid4(),
                title=todo_data.title,
                description=todo_data.description,
                completed=todo_data.completed,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Read existing data
            data = self._read_data()
            
            # Add new todo
            data.append(self._todo_to_dict(new_todo))
            
            # Write back to file
            self._write_data(data)
            
            return new_todo
    
    def get_all_todos(self, completed: Optional[bool] = None) -> List[Todo]:
        """Get all todos, optionally filtered by completion status"""
        with self._lock:
            data = self._read_data()
            todos = [self._dict_to_todo(item) for item in data]
            
            # Apply filter if specified
            if completed is not None:
                todos = [todo for todo in todos if todo.completed == completed]
            
            return todos
    
    def get_todo_by_id(self, todo_id: UUID) -> Optional[Todo]:
        """Get a specific todo by ID"""
        with self._lock:
            data = self._read_data()
            
            for item in data:
                if item.get('id') == str(todo_id):
                    return self._dict_to_todo(item)
            
            return None
    
    def update_todo(self, todo_id: UUID, todo_update: TodoUpdate) -> Optional[Todo]:
        """Update an existing todo"""
        with self._lock:
            data = self._read_data()
            
            for i, item in enumerate(data):
                if item.get('id') == str(todo_id):
                    # Update only provided fields
                    if todo_update.title is not None:
                        item['title'] = todo_update.title
                    if todo_update.description is not None:
                        item['description'] = todo_update.description
                    if todo_update.completed is not None:
                        item['completed'] = todo_update.completed
                    
                    # Always update timestamp
                    item['updated_at'] = datetime.now().isoformat()
                    
                    # Write back to file
                    self._write_data(data)
                    
                    return self._dict_to_todo(item)
            
            return None
    
    def delete_todo(self, todo_id: UUID) -> bool:
        """Delete a todo by ID. Returns True if deleted, False if not found"""
        with self._lock:
            data = self._read_data()
            
            for i, item in enumerate(data):
                if item.get('id') == str(todo_id):
                    data.pop(i)
                    self._write_data(data)
                    return True
            
            return False
    
    def toggle_completed(self, todo_id: UUID) -> Optional[Todo]:
        """Toggle the completed status of a todo"""
        with self._lock:
            data = self._read_data()
            
            for i, item in enumerate(data):
                if item.get('id') == str(todo_id):
                    # Toggle completed status
                    item['completed'] = not item['completed']
                    item['updated_at'] = datetime.now().isoformat()
                    
                    # Write back to file
                    self._write_data(data)
                    
                    return self._dict_to_todo(item)
            
            return None
    
    def count_todos(self) -> Dict[str, int]:
        """Get count statistics"""
        todos = self.get_all_todos()
        total = len(todos)
        completed = len([t for t in todos if t.completed])
        pending = total - completed
        
        return {
            'total': total,
            'completed': completed,
            'pending': pending
        }