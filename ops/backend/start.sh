#!/usr/bin/env bash
set -euo pipefail

# Start the Flask app via gunicorn from ops package
# Usage: ops/backend/start.sh [host] [port]
HOST=${1:-0.0.0.0}
PORT=${2:-5000}

if ! command -v pip >/dev/null 2>&1; then
  echo "pip not found. Please ensure Python is installed." >&2
  exit 1
fi

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
BACKEND_DIR=$(cd "$SCRIPT_DIR/../../backend" && pwd)
PROJECT_ROOT=$(cd "$BACKEND_DIR/.." && pwd)

pip install --upgrade pip >/dev/null
pip install -r "$BACKEND_DIR/requirements.txt"

export HOST
export PORT
export PYTHONPATH="$PROJECT_ROOT"
cd "$PROJECT_ROOT"

# Default workers: 2, can be overridden by env GUNICORN_WORKERS
WORKERS=${GUNICORN_WORKERS:-2}

exec gunicorn -w "$WORKERS" -b "$HOST:$PORT" backend.src.app
