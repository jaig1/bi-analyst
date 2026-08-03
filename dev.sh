#!/bin/bash
# Start backend (port 8000) and frontend (port 5173) for local development.
# Vite proxies /api/* → http://localhost:8000

export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"

# Kill any leftover processes on these ports
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null

echo "Starting FastAPI backend on :8000..."
python3 -m uvicorn api.index:app --reload --port 8000 &
BACKEND_PID=$!

echo "Starting Vite frontend on :5173..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "  Backend:  http://localhost:8000/api/health"
echo "  Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
