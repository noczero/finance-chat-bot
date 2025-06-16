#!/bin/bash

# Function to handle script termination
cleanup() {
    echo "Shutting down services..."
    kill $(jobs -p) 2>/dev/null
    exit
}

# Set up trap to catch termination signal
trap cleanup SIGINT SIGTERM

# Activate Python virtual environment
echo "Activating Python virtual environment..."
source .venv/bin/activate

# Start backend server
echo "Starting backend server..."
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Start frontend server
echo "Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "Both services are running!"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Press Ctrl+C to stop all services"

# Wait for both processes
wait
