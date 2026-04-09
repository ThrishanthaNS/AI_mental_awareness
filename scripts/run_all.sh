#!/bin/bash
# Run all services for AI Mental Awareness

echo "=== Starting AI Mental Awareness ==="

# Start backend
echo "[1/2] Starting FastAPI backend on port 8000..."
cd backend
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Start frontend
echo "[2/2] Starting React frontend on port 5173..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "=== All services running ==="
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all services."

# Wait and cleanup
trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM
wait
