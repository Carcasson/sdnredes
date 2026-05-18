#!/bin/bash
# ─────────────────────────────────────────────────────────────
#  build.sh — Script de Automatización
#  Extintores de Rivero SpA | WMS & Facturación SimpleAPI
#  Genera Dockerfile, construye imagen y ejecuta contenedor
# ─────────────────────────────────────────────────────────────

set -e

APP_NAME="extintores-rivero-app"
IMAGE_TAG="latest"
CONTAINER_NAME="samplerunning"

echo "=================================================="
echo "  Extintores de Rivero — Build & Deploy"
echo "=================================================="

# ── 1. Generar Dockerfile dinámicamente ──────────────────────
echo "[1/3] Generando Dockerfile..."

cat << 'DOCKERFILE' > Dockerfile
FROM python:3.10-slim

LABEL maintainer="Extintores de Rivero SpA"
LABEL description="Modulo WMS y Facturacion Electronica — SimpleAPI"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

CMD ["python", "app.py"]
DOCKERFILE

echo "      Dockerfile generado correctamente."

# ── 2. Construir imagen Docker ────────────────────────────────
echo ""
echo "[2/3] Construyendo imagen Docker: ${APP_NAME}:${IMAGE_TAG}..."
docker build -t "${APP_NAME}:${IMAGE_TAG}" .
echo "      Imagen construida exitosamente."

# ── 3. Ejecutar contenedor con variables de entorno seguras ──
# Las credenciales se inyectan desde el entorno — nunca hardcoded
echo ""
echo "[3/3] Ejecutando contenedor: ${CONTAINER_NAME}..."

docker run --name "${CONTAINER_NAME}" \
  -e SIMPLEAPI_TOKEN="${SIMPLEAPI_TOKEN}" \
  -e CERT_B64="${CERT_B64}" \
  -e CERT_PASSWORD="${CERT_PASSWORD}" \
  -e CAF_XML="${CAF_XML}" \
  -e EMISOR_RUT="${EMISOR_RUT}" \
  -e EMISOR_RAZON="${EMISOR_RAZON}" \
  -e EMISOR_GIRO="${EMISOR_GIRO}" \
  -e EMISOR_DIR="${EMISOR_DIR}" \
  -e EMISOR_COMUNA="${EMISOR_COMUNA}" \
  -e EMISOR_CIUDAD="${EMISOR_CIUDAD}" \
  -e ALERT_EMAIL="${ALERT_EMAIL}" \
  "${APP_NAME}:${IMAGE_TAG}"

echo ""
echo "=================================================="
echo "  Verificando estado del contenedor..."
echo "=================================================="
docker ps -a --filter "name=${CONTAINER_NAME}"
