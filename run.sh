#!/bin/bash
# Start the YouTube Music Downloader - one command, one URL.
# Usage: ./run.sh
# Then open http://localhost:8000

cd "$(dirname "$0")"

# Build frontend if needed
if [ ! -d "frontend/dist" ]; then
  echo "Building frontend (first time)..."
  (cd frontend && npm install && npm run build)
fi

echo "Starting server at http://localhost:8000"
echo "Press Ctrl+C to stop"
python api.py
