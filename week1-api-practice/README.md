# Todo API - Week 1 Agentic Coding Practice

A simple REST API for managing todo items, built using FastAPI as part of Week 1 agentic coding practice. This project demonstrates systematic development using the ai-dev-tasks workflow: PRD → Tasks → Implementation.

## Features

- Complete CRUD operations for todo items
- JSON file-based persistence with thread safety
- Automatic API documentation with OpenAPI/Swagger
- Comprehensive input validation using Pydantic
- Proper HTTP status codes and error handling
- Optional filtering by completion status
- Statistics endpoint for todo counts

## Project Structure

```
week1-api-practice/
├── main.py                    # FastAPI application and routes
├── models/
│   ├── __init__.py
│   └── todo.py               # Pydantic models for validation
├── storage/
│   ├── __init__.py
│   ├── todo_storage.py       # JSON file storage implementation
│   └── todos.json           # Data persistence file
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Test configuration and fixtures
│   ├── test_storage.py      # Unit tests for storage layer
│   └── test_endpoints.py    # Integration tests for API endpoints
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Installation and Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd week1-api-practice
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the API

1. **Start the server**
   ```bash
   python main.py
   ```
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access the API**
   - API Base URL: http://127.0.0.1:8000
   - Interactive Documentation: http://127.0.0.1:8000/docs
   - ReDoc Documentation: http://127.0.0.1:8000/redoc

## API Endpoints

### Root and Health
- `GET /` - API information and available endpoints
- `GET /health` - Health check with storage statistics

### Todo Operations
- `POST /api/todos` - Create a new todo
- `GET /api/todos` - List all todos (optional: `?completed=true/false`)
- `GET /api/todos/{id}` - Get a specific todo by ID
- `PUT /api/todos/{id}` - Update an existing todo
- `PATCH /api/todos/{id}/complete` - Toggle completion status
- `DELETE /api/todos/{id}` - Delete a todo

### Statistics
- `GET /api/stats` - Get todo count statistics

## Data Models

### Todo
```json
{
  "id": "uuid4",
  "title": "string (1-200 chars)",
  "description": "string (optional, max 1000 chars)",
  "completed": "boolean",
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)"
}
```

### Create Todo
```json
{
  "title": "string (required, 1-200 chars)",
  "description": "string (optional, max 1000 chars)",
  "completed": "boolean (default: false)"
}
```

### Update Todo
```json
{
  "title": "string (optional, 1-200 chars)",
  "description": "string (optional, max 1000 chars)",
  "completed": "boolean (optional)"
}
```

## Usage Examples

### Create a Todo
```bash
curl -X POST "http://127.0.0.1:8000/api/todos" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Learn FastAPI",
       "description": "Complete the todo API tutorial",
       "completed": false
     }'
```

### List All Todos
```bash
curl "http://127.0.0.1:8000/api/todos"
```

### List Only Completed Todos
```bash
curl "http://127.0.0.1:8000/api/todos?completed=true"
```

### Get a Specific Todo
```bash
curl "http://127.0.0.1:8000/api/todos/{todo-id}"
```

### Update a Todo
```bash
curl -X PUT "http://127.0.0.1:8000/api/todos/{todo-id}" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Updated title",
       "completed": true
     }'
```

### Toggle Completion Status
```bash
curl -X PATCH "http://127.0.0.1:8000/api/todos/{todo-id}/complete"
```

### Delete a Todo
```bash
curl -X DELETE "http://127.0.0.1:8000/api/todos/{todo-id}"
```

### Get Statistics
```bash
curl "http://127.0.0.1:8000/api/stats"
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test files
pytest tests/test_storage.py
pytest tests/test_endpoints.py

# Run with verbose output
pytest -v
```

### Test Coverage
- **Unit Tests**: Complete coverage of storage layer functionality
- **Integration Tests**: All API endpoints with valid and invalid scenarios
- **Error Handling**: Testing of all error conditions and edge cases
- **Validation**: Input validation and data integrity tests

## Error Handling

The API returns consistent error responses:

```json
{
  "detail": "Error message description"
}
```

### Common Status Codes
- `200` - Success
- `201` - Created successfully
- `204` - No content (successful deletion)
- `400` - Bad request (validation error)
- `404` - Resource not found
- `422` - Unprocessable entity (Pydantic validation)
- `500` - Internal server error

## Development Process

This project was built following the **Week 1 Agentic Coding workflow**:

1. **PRD Creation**: Detailed Product Requirements Document
2. **Task Generation**: Systematic breakdown into actionable tasks
3. **Implementation**: Step-by-step development with approval checkpoints
4. **Testing**: Comprehensive unit and integration tests
5. **Documentation**: Complete API documentation and usage examples

### Key Learning Outcomes
- Structured development with AI assistance
- Professional API design patterns
- Comprehensive testing strategies
- Clean code organization and documentation

## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI applications
- **Pydantic**: Data validation using Python type annotations
- **Pytest**: Testing framework
- **HTTPx**: HTTP client for testing (used by TestClient)

## Future Enhancements

Potential improvements for this API:
- Database integration (PostgreSQL, SQLite)
- User authentication and authorization
- Due dates and priority levels
- Todo categories and tags
- Search and advanced filtering
- Rate limiting and caching
- Docker containerization

## License

This project is part of the Week 1 agentic coding practice and is intended for educational purposes.