#!/bin/bash
# =============================================================================
# deploy.sh — Deployment script for kiro-django-demo-app
# Called by Jenkins during the 'deploy' stage
# Runs as: ubuntu (Jenkins agent = ubuntu user on the host)
# =============================================================================

set -e

APP_DIR="/var/www/kiro-django-demo-app"
VENV_DIR="${APP_DIR}/envs"
SERVICE_NAME="kiro-django-demo-app"
WORKSPACE_DIR="${WORKSPACE:-$(pwd)}"

echo ">>> [1/4] Copying code to ${APP_DIR}..."
rsync -a --exclude='envs/' \
         --exclude='.git/' \
         --exclude='__pycache__/' \
         "${WORKSPACE_DIR}/" "${APP_DIR}/"

echo ">>> [2/4] Installing dependencies..."
if [ ! -d "${VENV_DIR}" ]; then
    /usr/bin/python3.12 -m venv "${VENV_DIR}"
fi
"${VENV_DIR}/bin/pip" install --upgrade pip --quiet
"${VENV_DIR}/bin/pip" install -r "${APP_DIR}/requirements.txt" --quiet

echo ">>> [2b] Running Django migrations..."
cd "${APP_DIR}"
"${VENV_DIR}/bin/python" manage.py migrate --noinput

echo ">>> [3/4] Restarting application service..."
sudo systemctl restart "${SERVICE_NAME}"

echo ">>> [4/4] Verifying application is running..."
sleep 2
sudo systemctl is-active --quiet "${SERVICE_NAME}" && \
    echo "✅ Service ${SERVICE_NAME} is running" || \
    { echo "❌ Service ${SERVICE_NAME} failed to start"; sudo systemctl status "${SERVICE_NAME}" --no-pager; exit 1; }

echo ">>> Deployment complete — app accessible at http://$(hostname -I | awk '{print $1}'):8000"
