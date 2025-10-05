#!/bin/bash
echo "🚀 Starting FastAPI backend on Railway..."

# Ir a la carpeta del backend
cd backend

# Instalar dependencias
pip install --no-cache-dir -r requirements.txt

# Ejecutar la app con uvicorn
uvicorn api:app --host 0.0.0.0 --port $PORT
