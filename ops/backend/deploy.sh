#!/usr/bin/env bash
set -euo pipefail

# Triggers a deployment of the backend service on Render (DEV environment)
# Requires env var RENDER_BACKEND_DEV_HOOK to be set (a Deploy Hook URL from Render)

if [[ -z "${RENDER_BACKEND_DEV_HOOK:-}" ]]; then
  echo "RENDER_BACKEND_DEV_HOOK is not set" >&2
  exit 1
fi

curl -fsSv -X POST "$RENDER_BACKEND_DEV_HOOK"
echo "Triggered backend DEV deploy on Render"