#!/bin/bash

echo "Starting Wishlist Project..."

# Function to handle exit
cleanup() {
    echo ""
    echo "Stopping services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    exit 0
}

# Trap SIGINT (Ctrl+C) and SIGTERM to clean up background processes
trap cleanup SIGINT SIGTERM

echo "Starting Backend..."
cd src/backend || exit
# Using python3 instead of python for Mac/Linux compatibility
python3 -m uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ../..

echo "Starting Frontend..."
cd frontend || exit
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================================"
echo "Both services are running in the background."
echo "Press [Ctrl+C] to stop both services."
echo "========================================================"
echo ""

echo "Waiting for services to initialize..."
sleep 4

echo "Opening browser with default test user (test@example.com)..."
if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "http://localhost:5173" >/dev/null 2>&1
elif command -v open >/dev/null 2>&1; then
    open "http://localhost:5173" >/dev/null 2>&1
else
    echo "Could not auto-open browser. Please open: http://localhost:5173"
fi

# Wait for background processes to finish (which effectively waits for Ctrl+C)
wait
