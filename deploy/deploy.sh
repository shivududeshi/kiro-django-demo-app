#!/bin/bash
# =============================================================================
# deploy.sh — Deployment script for kiro-django-demo-app
# Called by Jenkins pipeline during the Deploy stage
# =============================================================================

set -e  # Exit immediately on any error

APP_DIR="/var/www/kiro-django-demo-app"
VENV_DIR="${APP_DIR}/envs"
WORKSPACE_DIR="${WORKSPACE:-$(pwd)}"
SERVICE_NAME="panorbit"

echo "========================================"
echo " kiro-django-demo-app Deployment Script"
echo "========================================"

# ── Step 1: Sync code to app directory ───────────────────────────────────────
echo "[1/6] Syncing code to ${APP_DIR}..."
sudo rsync -av --exclude='envs/' \
               --exclude='.git/' \
               --exclude='*.pyc' \
               --exclude='__pycache__/' \
               --exclude='staticfiles/' \
               --exclude='panorbit/whoosh_index/' \
               "${WORKSPACE_DIR}/" "${APP_DIR}/"

# ── Step 2: Set ownership ────────────────────────────────────────────────────
echo "[2/6] Setting file ownership..."
sudo chown -R ubuntu:ubuntu "${APP_DIR}"

# ── Step 3: Install/update dependencies ──────────────────────────────────────
echo "[3/6] Installing Python dependencies..."
if [ ! -d "${VENV_DIR}" ]; then
    /usr/bin/python3.12 -m venv "${VENV_DIR}"
fi
"${VENV_DIR}/bin/pip" install --upgrade pip
"${VENV_DIR}/bin/pip" install -r "${APP_DIR}/requirements.txt"

# ── Step 4: Django setup ──────────────────────────────────────────────────────
echo "[4/6] Running Django migrations and collecting static files..."
cd "${APP_DIR}"

# Load .env if present
if [ -f "${APP_DIR}/.env" ]; then
    export $(grep -v '^#' "${APP_DIR}/.env" | xargs)
fi

"${VENV_DIR}/bin/python" manage.py migrate --noinput
"${VENV_DIR}/bin/python" manage.py collectstatic --noinput

# ── Step 5: Restart Gunicorn service ─────────────────────────────────────────
echo "[5/6] Restarting Gunicorn service (${SERVICE_NAME})..."
sudo systemctl restart "${SERVICE_NAME}"
sudo systemctl status "${SERVICE_NAME}" --no-pager

# ── Step 6: Reload Nginx ──────────────────────────────────────────────────────
echo "[6/6] Reloading Nginx..."
sudo nginx -t
sudo systemctl reload nginx

echo "========================================"
echo " Deployment complete ✅"
echo " App running at: http://13.201.40.146"
echo "========================================"
