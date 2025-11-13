# Getting Started Guide

This guide will help you set up and run the AI development projects in this repository.

## Prerequisites

- Python 3.9 or higher
- Git
- OpenAI API key (for some projects)
- Google Gemini API key (for some projects)

## Quick Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Ncam00/ai-powerup-oct-25.git
cd ai-powerup-oct-25
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Setup
Create a `.env` file in each project directory with your API keys:
```bash
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
LANGFUSE_SECRET_KEY=your_langfuse_key_here  # Optional
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key_here  # Optional
```

## Project Demos

### Enhanced Chatbot (Week 2)
```bash
cd langchain-chatbot
streamlit run enhanced_app.py
```
- Features 5 personality modes
- Streaming responses
- Conversation memory

### AI Comedian (Week 2)
```bash
cd langchain-joke-teller
streamlit run app.py
```
- Multiple joke styles
- Topic-specific humor
- Favorites system

### Advanced Calculator (Week 1)
```bash
cd aice-calculator
python web_calculator.py
```
- Multi-step problem solving
- Tool integration
- Web interface

### Enhanced RAG System (Week 4)
```bash
cd week4-enhanced-rag
python rag_demo.py
```
- Vector database integration
- Document processing
- Evaluation framework

## Troubleshooting

### Common Issues

**Import Errors:**
```bash
pip install --upgrade -r requirements.txt
```

**API Key Issues:**
- Ensure your `.env` file is in the correct directory
- Verify API keys are valid and have sufficient credits

**Port Already in Use:**
```bash
# For Streamlit apps
streamlit run app.py --server.port 8502
```

**Database Connection (RAG System):**
```bash
# Ensure PostgreSQL is running
# Install PGVector extension if needed
```

## Development Setup

### Code Quality
```bash
# Format code
black .

# Lint code
flake8 .

# Run tests
pytest
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make changes
4. Run tests and linting
5. Submit a pull request

## Learning Path

1. **Week 1**: Agentic Coding - Start with calculator and API practice
2. **Week 2**: LLM Applications - Build chatbot and joke teller
3. **Week 3**: Production AI - Add structured output and observability
4. **Week 4**: RAG Systems - Implement enhanced retrieval
5. **Week 5-6**: Advanced Topics - Multimodal AI and agent systems

## Resources

- [LangChain Documentation](https://python.langchain.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## Support

- Open an issue for bugs or questions
- Check existing issues for common problems
- Review project READMEs for specific guidance

---

Happy coding! If you find this repository helpful, please star it and share with others learning AI development.