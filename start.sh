#!/bin/bash
echo "🚀 Starting FastAPI backend on Railway..."

python3 --version || echo "⚠️ Python3 not detected"
pip3 install --no-cache-dir -r backend/requirements.txt

cd backend
python3 -m uvicorn api:app --host 0.0.0.0 --port $PORT
