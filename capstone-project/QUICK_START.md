# Quick Start Guide - No Docker Required!

## 🚀 Running the Application

Since Docker isn't installed, here's how to run the capstone project using just Python:

### Step 1: Setup Environment

```bash
cd capstone-project

# Create .env file
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env  # or use your preferred editor
```

Add this line to `.env`:
```
OPENAI_API_KEY=sk-your-actual-openai-key-here
```

### Step 2: Install Dependencies

```bash
# Install backend dependencies
pip3 install -r requirements-backend.txt

# Install frontend dependencies
pip3 install -r requirements-frontend.txt
```

### Step 3: Run Backend (Terminal 1)

```bash
cd backend
python3 -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 4: Run Frontend (Terminal 2)

Open a **new terminal** and run:

```bash
cd capstone-project/frontend
streamlit run app.py --server.port 8501
```

You should see:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

### Step 5: Access the Application

- **Frontend (Main UI)**: http://localhost:8501
- **Backend API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 🎯 How It Works

### Architecture Overview

```
┌─────────────────┐         HTTP          ┌──────────────────┐
│   Streamlit     │  ◄──────────────────► │   FastAPI        │
│   Frontend      │    Port 8501/8000     │   Backend        │
│                 │                        │                  │
│  - Chat UI      │                        │  - API Routes    │
│  - Code Lab     │                        │  - Agents        │
│  - Quizzes      │                        │  - Tools         │
│  - Progress     │                        │  - RAG System    │
└─────────────────┘                        └──────────────────┘
                                                    │
                                                    ▼
                                           ┌──────────────────┐
                                           │  OpenAI API      │
                                           │  - GPT-4         │
                                           │  - Embeddings    │
                                           └──────────────────┘
```

### What Happens When You Use It

#### 1. Tutor Chat Tab
When you ask a question:
1. **Frontend** sends your message to `/api/v1/tutor/chat`
2. **Backend** receives request and invokes **Tutor Agent** (LangGraph)
3. **Agent** decides if it needs tools:
   - 🔍 Search Python documentation (RAG)
   - 💻 Execute code example
   - 📊 Analyze code quality
4. **Agent** uses GPT-4 to generate educational response
5. **Frontend** displays response with code examples

#### 2. Code Lab Tab
When you run code:
1. **Frontend** sends code to `/api/v1/code/execute`
2. **Backend** validates code (safety checks)
3. **Code Executor Tool** runs in sandboxed environment:
   - Restricted imports (only safe libraries)
   - 5-second timeout
   - Captures stdout/stderr
4. **Result** returned with output or error
5. **Frontend** displays formatted result

When you review code:
1. **Frontend** sends code to `/api/v1/code/review`
2. **Code Analyzer Tool** parses AST:
   - Checks function names
   - Validates docstrings
   - Measures complexity
   - Identifies issues
3. **Structured feedback** returned
4. **Frontend** shows score and suggestions

#### 3. Quiz Tab
When you generate a quiz:
1. **Frontend** sends topic to `/api/v1/quiz/generate`
2. **Quiz Generator Agent** uses GPT-4:
   - Creates questions based on topic
   - Adapts to difficulty level
   - Generates explanations
3. **Structured quiz** returned (JSON)
4. **Frontend** displays interactive quiz

#### 4. Progress Tab
Tracks your learning:
1. **Backend** stores session data (in-memory or database)
2. **Progress API** aggregates statistics
3. **Frontend** displays analytics

---

## 🛠️ Technology Stack Explained

### Frontend (Streamlit)
- **Why**: Rapid UI development, perfect for data/ML apps
- **Features**: 
  - Real-time updates
  - Interactive widgets
  - Built-in state management
  - Easy deployment

### Backend (FastAPI)
- **Why**: Modern, fast, automatic API docs
- **Features**:
  - Async support (handles multiple requests)
  - Pydantic validation (data safety)
  - OpenAPI docs (auto-generated)
  - Type hints (better code quality)

### AI Framework (LangGraph)
- **Why**: Explicit agent workflows, better control than pure LLM
- **Features**:
  - State machines for agents
  - Tool integration
  - Memory/checkpointing
  - Visual graph debugging

### Tools (LangChain)
- **Why**: Standard framework for AI tools
- **Features**:
  - Tool decorators
  - Structured outputs
  - Easy integration with LLMs

---

## 📊 Data Flow Example

Let's trace a complete interaction:

**User asks: "What is a list comprehension? Show me an example and run it."**

### Frontend (app.py)
```python
# 1. User types in chat
prompt = st.chat_input("Type your question...")

# 2. Send to backend
response = requests.post(
    "http://localhost:8000/api/v1/tutor/chat",
    json={
        "message": prompt,
        "session_id": "user123",
        "difficulty": "beginner"
    }
)

# 3. Display response
st.markdown(response.json()["message"])
```

### Backend API (routes/tutor.py)
```python
# 4. Receive request
@router.post("/chat")
async def tutor_chat(request: TutoringRequest):
    # 5. Call agent system
    result = await tutoring_system.tutor_student(
        message=request.message,
        session_id=request.session_id,
        difficulty=request.difficulty
    )
    return result
```

### Agent System (agents/tutor_agent.py)
```python
# 6. Agent reasoning (LangGraph)
async def tutor_node(state):
    # Bind tools to LLM
    llm_with_tools = llm.bind_tools([
        search_concepts,      # RAG search
        execute_python_code,  # Code runner
        analyze_code_quality  # Code review
    ])
    
    # 7. LLM decides to use tools
    response = llm_with_tools.invoke(messages)
    
    # 8. Execute tools if needed
    if response.tool_calls:
        # Call search_concepts("list comprehension")
        # Call execute_python_code("[x**2 for x in range(5)]")
    
    return {"messages": [response]}
```

### Tools
```python
# 9. Search tool executes
@tool
def search_concepts(query: str):
    # Search vector store or docs
    return "List comprehensions: [x for x in iterable]..."

# 10. Code executor runs
@tool
def execute_python_code(code: str):
    # Safety check
    if is_safe(code):
        result = exec(code)  # Sandboxed
        return f"Output: {result}"
```

### Final Response
```
Agent combines tool results with GPT-4 response:

"List comprehensions provide a concise way to create lists!

Here's the syntax:
```python
[expression for item in iterable if condition]
```

Let me show you an example:
```python
squares = [x**2 for x in range(5)]
```

I ran this code and got: [0, 1, 4, 9, 16]

Try modifying it to create cubes instead!"
```

---

## 🔧 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Use different port
uvicorn api.main:app --port 8001
```

### Frontend won't start
```bash
# Check if port 8501 is in use
lsof -i :8501

# Use different port
streamlit run app.py --server.port 8502
```

### API connection errors
Make sure:
1. Backend is running first
2. Frontend API_BASE_URL matches backend port
3. No firewall blocking localhost

### OpenAI API errors
Check:
1. API key is set in `.env`
2. API key is valid and has credits
3. No rate limiting (wait and retry)

---

## 🎯 Try These Examples

### 1. Ask the Tutor
```
"Explain Python functions with a simple example"
"What's the difference between lists and tuples?"
"Show me how to read a CSV file"
```

### 2. Code Lab
```python
# Try running this:
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

for i in range(10):
    print(fibonacci(i))
```

### 3. Generate Quiz
Topic: "Python Lists"
Difficulty: Medium
Questions: 5

---

## 📚 Learning Features

### Socratic Method
The tutor asks guiding questions instead of giving direct answers:
- "What do you think happens if...?"
- "Can you try modifying this code to...?"
- "Why do you think that error occurred?"

### Adaptive Difficulty
- **Beginner**: Simple language, lots of examples, very patient
- **Intermediate**: Technical terms, best practices focus
- **Advanced**: Precise terminology, optimization, design patterns

### Multi-Tool Integration
Agent can:
- Search documentation when you need reference
- Run code to demonstrate concepts
- Review your code for improvements
- Generate practice exercises

---

## 🚀 What Makes This Special

### Integration of All 6 Weeks

| Week | Technology | How It's Used |
|------|-----------|---------------|
| 1 | FastAPI | Backend API with 15+ endpoints |
| 2 | Prompts | Educational Socratic prompts |
| 3 | Tools | Code execution, analysis, search |
| 4 | RAG | Python documentation retrieval |
| 5 | Multimodal | Voice foundation (UI ready) |
| 6 | Agents | Multi-agent tutoring system |

### Production-Quality Features
- ✅ Error handling at every level
- ✅ Input validation (Pydantic)
- ✅ Safety (sandboxed code execution)
- ✅ Logging (debugging and monitoring)
- ✅ Type hints (code quality)
- ✅ Docstrings (self-documenting)
- ✅ Health checks (monitoring)
- ✅ Modular architecture (maintainable)

---

## 💡 Extending the Platform

Want to add features? Here's how:

### Add a New Tool
```python
# backend/tools/my_tool.py
from langchain_core.tools import tool

@tool
def my_new_tool(param: str) -> str:
    """Tool description for LLM"""
    # Your logic here
    return result

# backend/agents/tutor_agent.py
tools = [
    execute_python_code,
    search_concepts,
    my_new_tool  # Add here
]
```

### Add a New Agent
```python
# backend/agents/my_agent.py
class MySpecializedAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4")
    
    async def do_task(self, input: str):
        # Agent logic
        return result

# Integrate in tutor_agent.py
```

### Add a New Frontend Page
```python
# frontend/pages/my_page.py
import streamlit as st

st.title("My New Feature")
# Your UI here
```

---

**Enjoy building with AI!** 🎉
