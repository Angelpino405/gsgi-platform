#!/bin/bash
set -e
cd "$(dirname "$0")/backend"

echo "── GSGI Workforce Platform ──"
echo "Seeding database..."
python3 seed.py

echo "Starting server on http://localhost:8000"
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!
sleep 2

if command -v xdg-open &> /dev/null; then
  xdg-open http://localhost:8000
fi

echo "Server running (PID $SERVER_PID). Press Ctrl+C to stop."
trap "kill $SERVER_PID; echo 'Server stopped.'" INT TERM
wait $SERVER_PID
