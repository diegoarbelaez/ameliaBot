#!/bin/bash
# Script de inicio para Render.com
# Maneja la variable PORT correctamente

# Render proporciona PORT, si no existe usa 8000 por defecto
PORT=${PORT:-8000}

echo "🚀 Starting FastAPI application on port $PORT"

# Iniciar Uvicorn en el puerto correcto
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2

