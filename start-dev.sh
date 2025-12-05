#!/usr/bin/env bash
# Cross-platform dev orchestrator for Unix-like systems.
# Starts backend (uvicorn) and frontend (vite) in background and waits for backend /health.

set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

# Start backend in background
cd "$BACKEND_DIR"
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi
export PYTHONPATH="$BACKEND_DIR"
PORT=8000
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port $PORT &
BACKEND_PID=$!

echo "Started backend (pid=$BACKEND_PID). Waiting for /health..."

# Wait for health
for i in $(seq 1 30); do
    if curl -fsS --max-time 2 "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
        echo "Backend healthy"
        break
    fi
    sleep 1
done

# Start frontend
cd "$FRONTEND_DIR"
npm run dev &
FRONTEND_PID=$!

echo "Started frontend (pid=$FRONTEND_PID)."

echo "Dev servers started. Backend http://127.0.0.1:$PORT, Frontend http://localhost:5173"

echo "Press Ctrl+C to stop"
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; exit" SIGINT SIGTERM
wait
