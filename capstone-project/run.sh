#!/bin/bash
# Simple runner - starts both backend and frontend
# ================================================

echo "🚀 Starting AI Code Learning Platform..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ No .env file found!"
    echo "Run './setup.sh' first or create .env manually"
    exit 1
fi

# Check for OPENAI_API_KEY
if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "⚠️  Warning: OPENAI_API_KEY not set in .env"
    echo "Please edit .env and add your OpenAI API key"
    exit 1
fi

echo "✅ Environment configured"
echo ""

# Start backend in background
echo "🔧 Starting backend on http://localhost:8000..."
cd backend
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend on http://localhost:8501..."
cd frontend
streamlit run app.py --server.port 8501 &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Both services started!"
echo ""
echo "Access the application at:"
echo "  Frontend: http://localhost:8501"
echo "  Backend API: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
