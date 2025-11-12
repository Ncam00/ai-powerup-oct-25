# Task List: Todo API Implementation

Based on PRD: `0001-prd-todo-api.md`

## High-Level Tasks

### 1. Project Setup and Structure ✅
Set up the FastAPI project with proper directory structure, dependencies, and configuration files.

### 2. Data Models and Validation
Create Pydantic models for request/response validation and data structure definition.

### 3. Storage Layer Implementation
Implement JSON file-based storage system for todo persistence with CRUD operations.

### 4. API Endpoints Implementation
Develop all REST API endpoints with proper HTTP methods, status codes, and error handling.

### 5. Testing and Documentation
Create comprehensive tests for all endpoints and ensure API documentation is complete.

## Detailed Sub-Tasks

### 1. Project Setup and Structure
- [x] 1.1 Create project directory structure with app/, models/, storage/, tests/ folders
- [x] 1.2 Initialize virtual environment and install dependencies (fastapi, uvicorn, pydantic, pytest)
- [x] 1.3 Create main FastAPI application file with basic configuration
- [x] 1.4 Set up CORS middleware for frontend integration
- [x] 1.5 Create requirements.txt file with all dependencies

### 2. Data Models and Validation ✅
- [x] 2.1 Create Todo Pydantic model with validation rules (title, description, completed, timestamps)
- [x] 2.2 Create TodoCreate model for POST requests (excluding auto-generated fields)
- [x] 2.3 Create TodoUpdate model for PUT requests (all fields optional except ID)
- [x] 2.4 Create error response models for consistent error handling
- [x] 2.5 Add validation for title length (max 200 chars) and description (max 1000 chars)

### 3. Storage Layer Implementation ✅
- [x] 3.1 Create TodoStorage class with JSON file persistence
- [x] 3.2 Implement create_todo method with UUID generation and timestamps
- [x] 3.3 Implement get_all_todos method with optional completed filter
- [x] 3.4 Implement get_todo_by_id method with proper error handling
- [x] 3.5 Implement update_todo method with timestamp updates
- [x] 3.6 Implement delete_todo method with proper cleanup
- [x] 3.7 Add file locking for concurrent access safety
- [x] 3.8 Create initialize_storage method for first-run setup

### 4. API Endpoints Implementation ✅
- [x] 4.1 Implement POST /api/todos endpoint with validation and creation
- [x] 4.2 Implement GET /api/todos endpoint with optional filtering
- [x] 4.3 Implement GET /api/todos/{id} endpoint with 404 handling
- [x] 4.4 Implement PUT /api/todos/{id} endpoint with validation
- [x] 4.5 Implement PATCH /api/todos/{id}/complete endpoint for status toggle
- [x] 4.6 Implement DELETE /api/todos/{id} endpoint with proper status codes
- [x] 4.7 Add global exception handlers for consistent error responses
- [x] 4.8 Implement input validation with descriptive error messages

### 5. Testing and Documentation
- [ ] 5.1 Create test fixtures for sample todo data
- [ ] 5.2 Write unit tests for all TodoStorage methods
- [ ] 5.3 Write integration tests for all API endpoints
- [ ] 5.4 Test error cases and edge conditions (invalid IDs, missing data)
- [ ] 5.5 Verify OpenAPI documentation is complete and accurate
- [ ] 5.6 Create simple test runner script
- [ ] 5.7 Add README.md with setup and usage instructions

## Relevant Files

- `week1-api-practice/main.py` - Main FastAPI application and route definitions
- `week1-api-practice/models/todo.py` - Pydantic models for request/response validation
- `week1-api-practice/storage/todo_storage.py` - JSON file storage implementation
- `week1-api-practice/storage/todos.json` - JSON file for todo data persistence
- `week1-api-practice/tests/test_storage.py` - Unit tests for storage layer
- `week1-api-practice/tests/test_endpoints.py` - Integration tests for API endpoints
- `week1-api-practice/tests/conftest.py` - Test configuration and fixtures
- `week1-api-practice/requirements.txt` - Python dependencies
- `week1-api-practice/README.md` - Project documentation and setup instructions

## Notes

- Use FastAPI's automatic OpenAPI generation for documentation
- Start with simple JSON file storage - can upgrade to SQLite later
- Follow REST conventions for HTTP status codes (200, 201, 400, 404, 500)
- Include proper error handling with descriptive messages
- Use UUID for todo IDs to avoid collision issues
- Implement proper timestamp handling with ISO 8601 format
- Consider using file locking for thread safety in JSON storage

## Implementation Order

1. Start with project structure and basic FastAPI setup (1.1-1.5)
2. Define data models and validation (2.1-2.5)
3. Build storage layer with tests (3.1-3.8, 5.1-5.2)
4. Implement API endpoints one by one (4.1-4.8)
5. Complete testing and documentation (5.3-5.7)

This task list provides a systematic approach to building a production-ready todo API following Week 1's agentic coding principles.