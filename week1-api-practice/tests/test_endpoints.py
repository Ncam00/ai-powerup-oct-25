"""
Integration tests for API endpoints
"""

import pytest
from uuid import uuid4


class TestTodoAPI:
    """Integration tests for Todo API endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns API information"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "docs" in data
        assert "endpoints" in data
        
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "stats" in data
        
    def test_create_todo_valid(self, client, sample_todo_data):
        """Test creating a todo with valid data"""
        response = client.post("/api/todos", json=sample_todo_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == sample_todo_data["title"]
        assert data["description"] == sample_todo_data["description"]
        assert data["completed"] == sample_todo_data["completed"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        
    def test_create_todo_invalid_title_empty(self, client):
        """Test creating todo with empty title fails"""
        invalid_data = {"title": "", "description": "Valid description"}
        response = client.post("/api/todos", json=invalid_data)
        assert response.status_code == 422  # Validation error
        
    def test_create_todo_invalid_title_too_long(self, client):
        """Test creating todo with title too long fails"""
        invalid_data = {"title": "x" * 201, "description": "Valid description"}
        response = client.post("/api/todos", json=invalid_data)
        assert response.status_code == 422  # Validation error
        
    def test_create_todo_invalid_description_too_long(self, client):
        """Test creating todo with description too long fails"""
        invalid_data = {"title": "Valid title", "description": "x" * 1001}
        response = client.post("/api/todos", json=invalid_data)
        assert response.status_code == 422  # Validation error
        
    def test_list_todos_empty(self, client):
        """Test listing todos when storage is empty"""
        response = client.get("/api/todos")
        assert response.status_code == 200
        
        data = response.json()
        assert data["todos"] == []
        assert data["total"] == 0
        assert data["filtered"] == False
        
    def test_list_todos_with_data(self, client, sample_todos):
        """Test listing todos with data"""
        # Create sample todos
        created_ids = []
        for todo_data in sample_todos:
            response = client.post("/api/todos", json=todo_data)
            assert response.status_code == 201
            created_ids.append(response.json()["id"])
        
        # List all todos
        response = client.get("/api/todos")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["todos"]) == 3
        assert data["total"] == 3
        assert data["filtered"] == False
        
    def test_list_todos_filtered_completed(self, client, sample_todos):
        """Test listing todos filtered by completed status"""
        # Create sample todos
        for todo_data in sample_todos:
            response = client.post("/api/todos", json=todo_data)
            assert response.status_code == 201
        
        # List only completed todos
        response = client.get("/api/todos?completed=true")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["todos"]) == 1  # Only "Second Todo" is completed
        assert data["todos"][0]["title"] == "Second Todo"
        assert data["todos"][0]["completed"] == True
        assert data["filtered"] == True
        
        # List only pending todos
        response = client.get("/api/todos?completed=false")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["todos"]) == 2
        assert data["filtered"] == True
        
    def test_get_todo_existing(self, client, sample_todo_data):
        """Test getting an existing todo by ID"""
        # Create a todo
        create_response = client.post("/api/todos", json=sample_todo_data)
        assert create_response.status_code == 201
        created_todo = create_response.json()
        todo_id = created_todo["id"]
        
        # Get the todo
        response = client.get(f"/api/todos/{todo_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == todo_id
        assert data["title"] == sample_todo_data["title"]
        
    def test_get_todo_non_existent(self, client):
        """Test getting a non-existent todo returns 404"""
        fake_id = str(uuid4())
        response = client.get(f"/api/todos/{fake_id}")
        assert response.status_code == 404
        
    def test_get_todo_invalid_id(self, client):
        """Test getting todo with invalid ID format returns 400"""
        response = client.get("/api/todos/invalid-uuid")
        assert response.status_code == 422  # FastAPI validation error
        
    def test_update_todo_existing(self, client, sample_todo_data):
        """Test updating an existing todo"""
        # Create a todo
        create_response = client.post("/api/todos", json=sample_todo_data)
        assert create_response.status_code == 201
        created_todo = create_response.json()
        todo_id = created_todo["id"]
        
        # Update the todo
        update_data = {
            "title": "Updated Title",
            "description": "Updated description",
            "completed": True
        }
        response = client.put(f"/api/todos/{todo_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated description"
        assert data["completed"] == True
        assert data["updated_at"] > created_todo["updated_at"]
        
    def test_update_todo_partial(self, client, sample_todo_data):
        """Test partial update of a todo"""
        # Create a todo
        create_response = client.post("/api/todos", json=sample_todo_data)
        assert create_response.status_code == 201
        created_todo = create_response.json()
        todo_id = created_todo["id"]
        
        # Partial update
        update_data = {"title": "Only Title Changed"}
        response = client.put(f"/api/todos/{todo_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Only Title Changed"
        assert data["description"] == sample_todo_data["description"]  # Unchanged
        assert data["completed"] == sample_todo_data["completed"]  # Unchanged
        
    def test_update_todo_non_existent(self, client):
        """Test updating a non-existent todo returns 404"""
        fake_id = str(uuid4())
        update_data = {"title": "Should not work"}
        response = client.put(f"/api/todos/{fake_id}", json=update_data)
        assert response.status_code == 404
        
    def test_toggle_todo_complete(self, client, sample_todo_data):
        """Test toggling todo completion status"""
        # Create a todo (initially not completed)
        create_response = client.post("/api/todos", json=sample_todo_data)
        assert create_response.status_code == 201
        created_todo = create_response.json()
        todo_id = created_todo["id"]
        assert created_todo["completed"] == False
        
        # Toggle to completed
        response = client.patch(f"/api/todos/{todo_id}/complete")
        assert response.status_code == 200
        
        data = response.json()
        assert data["completed"] == True
        assert data["updated_at"] > created_todo["updated_at"]
        
        # Toggle back to not completed
        response = client.patch(f"/api/todos/{todo_id}/complete")
        assert response.status_code == 200
        
        data = response.json()
        assert data["completed"] == False
        
    def test_toggle_todo_complete_non_existent(self, client):
        """Test toggling completion of non-existent todo returns 404"""
        fake_id = str(uuid4())
        response = client.patch(f"/api/todos/{fake_id}/complete")
        assert response.status_code == 404
        
    def test_delete_todo_existing(self, client, sample_todo_data):
        """Test deleting an existing todo"""
        # Create a todo
        create_response = client.post("/api/todos", json=sample_todo_data)
        assert create_response.status_code == 201
        created_todo = create_response.json()
        todo_id = created_todo["id"]
        
        # Verify todo exists
        response = client.get(f"/api/todos/{todo_id}")
        assert response.status_code == 200
        
        # Delete the todo
        response = client.delete(f"/api/todos/{todo_id}")
        assert response.status_code == 204
        assert response.content == b""  # No content for 204
        
        # Verify todo no longer exists
        response = client.get(f"/api/todos/{todo_id}")
        assert response.status_code == 404
        
    def test_delete_todo_non_existent(self, client):
        """Test deleting a non-existent todo returns 404"""
        fake_id = str(uuid4())
        response = client.delete(f"/api/todos/{fake_id}")
        assert response.status_code == 404
        
    def test_stats_endpoint(self, client, sample_todos):
        """Test statistics endpoint"""
        # Create sample todos
        for todo_data in sample_todos:
            response = client.post("/api/todos", json=todo_data)
            assert response.status_code == 201
        
        # Get stats
        response = client.get("/api/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 3
        assert data["completed"] == 1
        assert data["pending"] == 2
        
    def test_api_documentation_accessible(self, client):
        """Test that API documentation is accessible"""
        response = client.get("/docs")
        assert response.status_code == 200
        
        response = client.get("/redoc")
        assert response.status_code == 200