# Capstone Project: AI Code Learning Platform

## 🎯 Project Overview

An advanced AI-powered learning platform that combines **all techniques from Weeks 1-6** into a comprehensive, production-ready application for learning Python programming.

## 🏗️ Architecture

This capstone integrates:
- **Week 1**: REST API fundamentals (FastAPI backend)
- **Week 2**: Advanced prompt engineering (educational prompts)
- **Week 3**: Tool use & structured outputs (code execution, analysis)
- **Week 4**: RAG system (Python documentation retrieval)
- **Week 5**: Multimodal AI (voice tutoring, code visualization)
- **Week 6**: Agent-based systems (autonomous tutoring agent)

## 📁 Project Structure

```
capstone-project/
├── backend/                    # FastAPI REST API
│   ├── api/
│   │   ├── routes/            # API endpoints
│   │   ├── models/            # Data models
│   │   └── middleware/        # Auth, logging, etc.
│   ├── agents/                # AI agents
│   │   ├── tutor_agent.py    # Main teaching agent
│   │   ├── code_reviewer.py  # Code analysis agent
│   │   └── quiz_generator.py # Assessment agent
│   ├── tools/                 # Agent tools
│   │   ├── code_executor.py  # Safe Python execution
│   │   ├── concept_search.py # RAG retrieval
│   │   └── visualizer.py     # Code visualization
│   └── rag/                   # RAG system
│       ├── embeddings/        # Vector storage
│       └── retrieval/         # Search logic
├── frontend/                  # Streamlit UI
│   ├── pages/
│   │   ├── chat.py           # Main tutoring interface
│   │   ├── code_lab.py       # Interactive coding
│   │   ├── quiz.py           # Assessments
│   │   └── progress.py       # Learning analytics
│   └── components/
│       ├── voice_input.py    # Speech-to-text
│       ├── code_editor.py    # Syntax highlighting
│       └── visualizations.py # Charts and diagrams
├── knowledge_base/            # Python documentation
│   ├── raw/                  # Original docs
│   ├── processed/            # Chunked for RAG
│   └── embeddings/           # Vector store
├── tests/                     # Comprehensive testing
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docker/                    # Containerization
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
├── .env.example
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## ✨ Features

### Core Learning Features
- **Interactive Tutoring**: Multi-agent system for personalized teaching
- **Code Execution**: Safe sandboxed Python code running
- **Concept Search**: RAG-powered Python documentation retrieval
- **Voice Interface**: Speech-to-text and text-to-speech tutoring
- **Code Review**: Automated feedback on student code
- **Quiz Generation**: Dynamic assessments based on learning progress

### Advanced Features
- **Human-in-the-Loop**: Teacher can intervene in agent decisions
- **Multi-Agent Coordination**: Tutor, reviewer, and quiz agents collaborate
- **Persistent Memory**: Tracks student progress across sessions
- **Adaptive Difficulty**: Adjusts based on performance
- **Code Visualization**: Execution flow diagrams
- **Real-time Collaboration**: Multiple students can learn together

## 🚀 Getting Started

### Prerequisites
```bash
Python 3.10+
Docker & Docker Compose
OpenAI API key
ElevenLabs API key (optional, for voice)
```

### Installation

1. **Clone and setup**:
```bash
cd capstone-project
cp .env.example .env
# Edit .env with your API keys
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Initialize knowledge base**:
```bash
python scripts/build_knowledge_base.py
```

4. **Run with Docker** (recommended):
```bash
docker-compose up
```

5. **Or run locally**:
```bash
# Terminal 1: Backend
cd backend && uvicorn api.main:app --reload

# Terminal 2: Frontend
cd frontend && streamlit run app.py
```

### Access
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# With coverage
pytest --cov=backend --cov=frontend --cov-report=html
```

## 📊 Technical Highlights

### Week 1: REST API Architecture
- FastAPI backend with async endpoints
- Request/response validation with Pydantic
- JWT authentication
- Rate limiting and CORS

### Week 2: Prompt Engineering
- Educational prompt templates
- Socratic questioning system
- Difficulty-adaptive prompts
- Multi-turn conversation management

### Week 3: Tool Use & Structured Output
- Safe code execution tool
- Code analysis tool (AST parsing)
- Concept retrieval tool
- Quiz generation with structured schemas

### Week 4: RAG Implementation
- Python documentation embedded (ChromaDB)
- Hybrid search (semantic + keyword)
- Re-ranking for relevance
- Citation tracking

### Week 5: Multimodal Capabilities
- Voice input (Whisper STT)
- Voice output (ElevenLabs/OpenAI TTS)
- Code visualization (execution diagrams)
- Interactive code editor

### Week 6: Agent-Based System
- **Tutor Agent**: Main teaching orchestrator
- **Code Reviewer**: Analyzes and provides feedback
- **Quiz Generator**: Creates assessments
- **Coordinator**: Routes between specialists
- Human-in-the-loop for complex decisions

## 🎓 Learning Outcomes Demonstrated

✅ **API Development**: Production-ready REST API  
✅ **Prompt Engineering**: Educational AI interactions  
✅ **Tool Integration**: Custom tools for code execution  
✅ **RAG Systems**: Knowledge retrieval from documentation  
✅ **Multimodal AI**: Voice and visual learning  
✅ **Agent Architecture**: Multi-agent coordination  
✅ **Testing**: Comprehensive test coverage  
✅ **DevOps**: Docker, CI/CD ready  
✅ **Security**: Safe code execution, authentication  
✅ **UX Design**: Intuitive learning interface  

## 📈 Future Enhancements

- [ ] Multi-language support (JavaScript, Java, etc.)
- [ ] Peer learning (student-to-student matching)
- [ ] Video tutorials generation
- [ ] Live coding sessions with screen sharing
- [ ] Mobile app (React Native)
- [ ] LMS integration (Canvas, Moodle)
- [ ] Gamification (badges, leaderboards)
- [ ] AI-generated coding challenges
- [ ] Career guidance integration

## 🤝 Contributing

This is a capstone project demonstrating skills from AI Coding Essentials course. Contributions welcome!

## 📄 License

MIT License - see LICENSE file

## 🙏 Acknowledgments

Built as capstone project for AI Coding Essentials course, integrating techniques from:
- Week 1: API Fundamentals
- Week 2: Prompt Engineering
- Week 3: Tool Use & Structured Outputs
- Week 4: RAG Systems
- Week 5: Multimodal AI
- Week 6: Agent-Based Systems

---

**Status**: 🚧 In Development  
**Created**: November 21, 2024  
**Author**: AI Coding Essentials Student
