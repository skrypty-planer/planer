#!/usr/bin/env bash
set -euo pipefail

# Triggers a deployment of the frontend static site on Render (DEV)
# Requires env var RENDER_FRONTEND_DEV_HOOK (a Deploy Hook URL from Render)

if [[ -z "${RENDER_FRONTEND_DEV_HOOK:-}" ]]; then
  echo "RENDER_FRONTEND_DEV_HOOK is not set" >&2
  exit 1
fi

curl -fsS -X POST "$RENDER_FRONTEND_DEV_HOOK"
echo "Triggered frontend DEV deploy on Render"