#!/usr/bin/env bash
set -euo pipefail

export HOST="${HOST:-0.0.0.0}"
export BACKEND_PORT="${BACKEND_PORT:-8000}"
export FRONTEND_PORT="${FRONTEND_PORT:-5173}"
export VITE_API_BASE_URL="${VITE_API_BASE_URL:-http://localhost:${BACKEND_PORT}}"
export CORS_ORIGINS="${CORS_ORIGINS:-http://localhost:${FRONTEND_PORT},http://127.0.0.1:${FRONTEND_PORT}}"

echo "Installing backend dependencies..."
cd backend
python -m pip install -r requirements.txt
python seed_demo_data.py
RELOAD=false HOST="$HOST" PORT="$BACKEND_PORT" python run_backend.py &
BACKEND_PID=$!
trap "kill $BACKEND_PID" EXIT
cd ..

echo "Installing frontend dependencies..."
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port "$FRONTEND_PORT"
