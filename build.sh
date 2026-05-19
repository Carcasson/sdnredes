#!/bin/bash
set -e

APP_NAME="extintores-rivero-app"
CONTAINER_NAME="samplerunning"

echo "=================================================="
echo "  Extintores de Rivero — Build & Deploy v3.0"
echo "=================================================="

# Generar Dockerfile
cat > Dockerfile << 'DOCKERFILE'
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
CMD ["python", "app.py"]
DOCKERFILE

echo "[1/3] Dockerfile generado"

# Construir imagen
echo "[2/3] Construyendo imagen Docker..."
docker build -t "${APP_NAME}:latest" .

# Ejecutar contenedor
echo "[3/3] Ejecutando contenedor..."
docker run --name "${CONTAINER_NAME}" \
  -e DEMO_MODE="true" \
  "${APP_NAME}:latest"

echo ""
echo "=================================================="
docker ps -a --filter "name=${CONTAINER_NAME}"
echo "=================================================="
