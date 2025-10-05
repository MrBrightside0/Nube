#!/bin/bash
echo "🚀 Starting FastAPI backend on Railway..."

# Mostrar versión de Python (para debug)
python3 --version

# Instalar dependencias
pip3 install --no-cache-dir -r backend/requirements.txt

# Ir a la carpeta del backend
cd backend

# Ejecutar FastAPI
python3 -m uvicorn api:app --host 0.0.0.0 --port $PORT
