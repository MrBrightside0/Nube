#!/bin/bash
echo "🚀 Starting FastAPI backend on Railway..."

# Muestra versión de Python
python3 --version

# Instala dependencias
pip install --no-cache-dir -r backend/requirements.txt

# Entra al backend
cd backend

# Ejecuta FastAPI
python3 -m uvicorn api:app --host 0.0.0.0 --port $PORT
