#!/usr/bin/env bash
# start.sh — Start Veritas backend + frontend in one command

set -e

echo "⚖  Veritas — Starting up..."
echo ""

# ── Backend ──────────────────────────────────────
echo "► Starting backend..."
cd backend

if [ ! -d "venv" ]; then
  echo "  Creating virtual environment..."
  python3 -m venv venv
fi

source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

echo "  Installing dependencies..."
pip install -q -r requirements.txt

echo "  Launching FastAPI on http://localhost:8000"
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

cd ..

# ── Frontend ─────────────────────────────────────
echo "► Starting frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
  echo "  Installing npm packages..."
  npm install
fi

echo "  Launching React on http://localhost:3000"
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "✅ Veritas is running!"
echo "   Frontend → http://localhost:3000"
echo "   Backend  → http://localhost:8000"
echo "   API Docs → http://localhost:8000/api/docs"
echo ""
echo "Press Ctrl+C to stop both servers."

# Wait and cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Stopped.'" EXIT
wait
