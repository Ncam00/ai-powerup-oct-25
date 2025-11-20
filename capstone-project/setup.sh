#!/bin/bash
# Quick Start Script - Run without Docker
# ==========================================

echo "🚀 Starting AI Code Learning Platform..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Creating .env file from template..."
    cp .env.example .env
    echo "📝 Please edit .env and add your OPENAI_API_KEY"
    echo ""
    read -p "Press Enter after adding your API key..."
fi

# Install backend dependencies
echo ""
echo "📦 Installing backend dependencies..."
cd backend
pip3 install -q -r ../requirements-backend.txt 2>&1 | grep -v "already satisfied" || true

# Install frontend dependencies  
echo "📦 Installing frontend dependencies..."
cd ../frontend
pip3 install -q -r ../requirements-frontend.txt 2>&1 | grep -v "already satisfied" || true

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 To run the application:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd capstone-project/backend"
echo "  python3 -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd capstone-project/frontend"
echo "  streamlit run app.py --server.port 8501"
echo ""
echo "Then access:"
echo "  Frontend: http://localhost:8501"
echo "  Backend API Docs: http://localhost:8000/docs"
echo ""
