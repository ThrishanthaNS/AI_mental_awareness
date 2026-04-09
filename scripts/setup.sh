#!/bin/bash
# Setup script for AI Mental Awareness project

echo "=== AI Mental Awareness - Setup ==="

# Backend setup
echo "[1/3] Setting up backend..."
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..

# ML setup
echo "[2/3] Setting up ML environment..."
cd ml
pip install -r requirements.txt
cd ..

# Frontend setup
echo "[3/3] Setting up frontend..."
cd frontend
npm install
cd ..

echo "=== Setup complete! ==="
echo "Run './scripts/run_all.sh' to start the application."
