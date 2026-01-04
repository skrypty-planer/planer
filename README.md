### Password Generator App (Flask backend + Vue frontend)

A minimal full‑stack password generator:
- Backend: Python Flask with a `@singleton`-based Singleton pattern and `/api/v1/password` endpoint
- Frontend: Vue 3 + Vite, calling the backend API
- CI: GitHub Actions for backend and frontend (tests, build, smoke)
- CD: Deploy pipelines (dev/prod) triggering Render deploy hooks via bash scripts
- Render: `render.yaml` blueprint for easy provisioning

---

### Architecture highlights
- Singleton pattern implemented via `@singleton` decorator in `backend/decorators.py`.
  - Classes that need singletons are annotated with `@singleton` and must be accessed using `ClassName.get_instance()`.
  - Implemented singletons:
    - `backend/config.py` → `Config.get_instance()`
    - `backend/services/password_service.py` → `PasswordService.get_instance()`
- Flask app factory in `backend/app.py` with endpoints:
  - `GET /health` → `{ status: "ok" }`
  - `GET /api/v1/password` → `{ password: "..." }`
    - Query params: `length`, `lowercase`, `uppercase`, `digits`, `symbols` (booleans accepted: `1/0`, `true/false`, `yes/no`, `on/off`).
- CORS enabled (allow all by default; configurable via env vars).

---

### Backend (Python/Flask)
- Code: `backend/`
- Entrypoint: `backend/app.py` (WSGI app `backend.app:app`)
- Requirements: `backend/requirements.txt`
- Scripts: `ops/backend/`
  - `start.sh` → install deps and run gunicorn
  - `test.sh` → install deps and run pytest
  - `smoke.sh` → start server and validate `/health` and `/api/v1/password`
  - `deploy-*.sh` → call Render deploy hooks for dev/prod

Local run (backend):
```
# from repo root
bash ops/backend/start.sh 0.0.0.0 5000
# or for quick dev: python -m flask --app backend.app:app run -p 5000
```

Unit tests:
```
bash ops/backend/test.sh
```

Smoke test:
```
PORT=5050 bash ops/backend/smoke.sh
```

Backend environment variables (optional):
- `HOST` (default `0.0.0.0`)
- `PORT` (default `5000`)
- `FLASK_DEBUG` (default `false`)
- `CORS_ALLOW_ALL` (default `true`)
- `CORS_ORIGINS` (comma-separated, used when `CORS_ALLOW_ALL=false`)
- `PW_DEFAULT_LENGTH` (default `16`)
- `PW_MIN_LENGTH` (default `4`)
- `PW_MAX_LENGTH` (default `128`)
- `PW_ALLOW_LOWERCASE|UPPERCASE|DIGITS|SYMBOLS` (all default `true`)

---

### Frontend (Vue 3 + Vite)
- Code: `frontend/`
- Main files: `index.html`, `src/App.vue`, `src/components/PasswordGenerator.vue`
- Config: `frontend/vite.config.js`
- Env example: `frontend/.env.example`
- Scripts: `ops/frontend/`
  - `smoke.sh` → mocked smoke only (no network/preview); build is validated in the Build stage
  - `deploy-*.sh` → call Render deploy hooks for dev/prod
  - `slot-swap-sim.sh` → simulate blue/green slot switching (prepare/promote/rollback)
  - `test-functional-sim.sh` → simulate functional tests (~60s default)
  - `test-performance-sim.sh` → simulate performance tests (~60s default)

Local run (frontend):
```
cd frontend
cp .env.example .env  # optionally set VITE_API_BASE_URL=http://localhost:5000
npm i
npm run dev
```
The app expects `VITE_API_BASE_URL` to point to the backend (defaults to `http://localhost:5000`).

Build locally:
```
npm run build
npm run preview
```

---

### GitHub Actions (CI/CD)
Workflows are under `.github/workflows/`:
- `backend-ci.yml`:
  - Python 3.14
  - Runs `ops/backend/test.sh` and `ops/backend/smoke.sh`
- `frontend-ci.yml`:
  - Node 20
  - Runs `ops/frontend/smoke.sh`
- `backend-deploy.yml` and `frontend-deploy.yml`:
  - Trigger on pushes to branches: `dev`, `main`
  - Call corresponding `deploy-*.sh` in `ops/` with Render deploy hooks

Set GitHub repository secrets for deploy hooks:
- Backend:
  - `RENDER_BACKEND_DEV_HOOK`
  - `RENDER_BACKEND_PROD_HOOK`
- Frontend:
  - `RENDER_FRONTEND_DEV_HOOK`
  - `RENDER_FRONTEND_PROD_HOOK`

How to obtain Render Deploy Hooks:
- In Render dashboard → Your service → Settings → Deploy hooks → Create Hook.
- Paste the hook URLs into GitHub → Settings → Secrets and variables → Actions → New repository secret.

Branch to environment mapping:
- `dev` branch → DEV hooks
- `main` branch → PROD hooks

---

### Render deployment
Option A — Render Blueprint (recommended):
- File: `render.yaml` includes both backend (web) and frontend (static) services.
- In Render, create a Blueprint from your repo.
- Backend service:
  - Build command: `pip install -r backend/requirements.txt`
  - Start command: `gunicorn -w 2 -b 0.0.0.0:$PORT backend.app:app`
  - Health check: `/health`
  - Env vars: already shown in `render.yaml` (you can customize).
- Frontend service (Static Site):
  - Build command: `cd frontend && npm ci && npm run build`
  - Publish directory: `frontend/dist`
  - After backend is deployed, set `VITE_API_BASE_URL` to the backend’s public URL (e.g., `https://password-generator-backend.onrender.com`).

Option B — Manual services:
- Create a new Web Service for backend (from repo):
  - Root directory
  - Build command and Start command as above
  - Health check path `/health`
- Create a Static Site for frontend:
  - Build command: `cd frontend && npm ci && npm run build`
  - Publish `frontend/dist`
  - Set `VITE_API_BASE_URL` to backend URL

After first deploy:
- Visit the frontend URL; generating a password should call the backend API and display the result.

---

### API usage examples
```
# Default options
curl 'http://localhost:5000/api/v1/password'

# Custom options
curl 'http://localhost:5000/api/v1/password?length=24&digits=true&symbols=true&uppercase=true&lowercase=false'
```
Responses:
```
{ "password": "Ab3..." }
```
Errors (HTTP 400):
```
{ "error": "length must be between 4 and 128" }
```

---

### Project structure
```
backend/
  __init__.py
  app.py
  config.py
  decorators.py
  requirements.txt
  services/
    __init__.py
    password_service.py
  tests/
    test_password_service.py
frontend/
  index.html
  package.json
  vite.config.js
  .env.example
  src/
    main.js
    App.vue
    components/
      PasswordGenerator.vue
ops/
  backend/
    start.sh
    test.sh
    smoke.sh
    deploy-dev.sh
    deploy-prod.sh
    slot-swap-sim.sh
    test-functional-sim.sh
    test-performance-sim.sh
  frontend/
    smoke.sh
    deploy-dev.sh
    deploy-prod.sh
    slot-swap-sim.sh
    test-functional-sim.sh
    test-performance-sim.sh
.github/
  workflows/
    backend-ci.yml
    backend-deploy.yml
    frontend-ci.yml
    frontend-deploy.yml
render.yaml
README.md
```

---

### Notes
- The Singleton pattern is centralized in `backend/decorators.py` and used via `@singleton`. Classes that require singleton access expose `ClassName.get_instance()` automatically.
- Default CORS allows all origins; restrict via `CORS_ALLOW_ALL=false` + `CORS_ORIGINS`.
- The password generator ensures at least one character from each enabled class is present and shuffles for randomness.
- CI smoke tests rely on `curl` and `jq` (installed in the workflow).

---

### Troubleshooting
- 403 CORS errors in the browser: set correct `CORS_*` env vars on the backend service and ensure `VITE_API_BASE_URL` matches the backend public URL.
- Frontend cannot reach backend on Render: confirm backend is healthy (`/health`), and `VITE_API_BASE_URL` is configured.
- GitHub deploy workflows not firing: ensure you push to branches `dev`, `test`, or `main`, and secrets are set.


### Step-by-step: Configure VITE_API_BASE_URL_DEV/PROD on Render and Deploy Hook secrets in GitHub

This section walks you through setting the three frontend API base variables and the four Render Deploy Hook secrets, end-to-end for Dev and Prod.

Key variables and secrets you will set:
- Frontend env vars (Render Static Site services):
  - VITE_API_BASE_URL_DEV (on the Dev frontend)
  - VITE_API_BASE_URL_PROD (on the Prod frontend)
  - VITE_API_BASE_URL (optional local fallback; used in local .env only)
- GitHub repository secrets (used by workflows in .github/workflows/*-deploy.yml):
  - RENDER_BACKEND_DEV_HOOK
  - RENDER_BACKEND_PROD_HOOK
  - RENDER_FRONTEND_DEV_HOOK
  - RENDER_FRONTEND_PROD_HOOK

Prerequisites
- Two environments on Render created from this repo (via render.yaml Blueprint or manual):
  - Dev: services named like password-generator-backend-dev and password-generator-frontend-dev on branch dev
  - Prod: services named like password-generator-backend-prod and password-generator-frontend-prod on branch main
- You know the branch mapping: dev → Dev, main → Prod.

1) Get backend public URLs on Render (Dev and Prod)
- Render Dashboard → Your Dev backend service (e.g., password-generator-backend-dev)
  - Copy the public URL from the service header (looks like https://<backend-dev>.onrender.com)
- Render Dashboard → Your Prod backend service (e.g., password-generator-backend-prod)
  - Copy its public URL (https://<backend-prod>.onrender.com)

2) Set frontend API base variables on Render Static Sites
Do this separately for Dev and Prod frontend services.
- Dev frontend:
  - Render Dashboard → password-generator-frontend-dev → Settings → Environment → Environment Variables
  - Add key: VITE_API_BASE_URL_DEV
  - Value: the Dev backend URL you copied in step 1 (e.g., https://<backend-dev>.onrender.com)
  - Save changes
  - Redeploy the Dev frontend so the value is baked into the build (Static Sites read env vars at build time)
- Prod frontend:
  - Render Dashboard → password-generator-frontend-prod → Settings → Environment → Environment Variables
  - Add key: VITE_API_BASE_URL_PROD
  - Value: the Prod backend URL from step 1
  - Save changes and redeploy the Prod frontend
Notes:
- The app resolves API base in this order: VITE_API_BASE_URL_PROD → VITE_API_BASE_URL_DEV → VITE_API_BASE_URL → http://localhost:5000.
- For local development only, set VITE_API_BASE_URL in frontend/.env (not in Render). See frontend/.env.example.

3) Create Deploy Hooks on Render for all four services
You will generate one Deploy Hook URL per service, then store each in GitHub as a secret.
- For each Render service (Dev backend, Prod backend, Dev frontend, Prod frontend):
  - Render Dashboard → Service → Settings → Deploy hooks → Create Hook
  - Copy the URL shown; you will paste it into GitHub in the next step
  - Recommended mapping:
    - Dev backend → RENDER_BACKEND_DEV_HOOK
    - Prod backend → RENDER_BACKEND_PROD_HOOK
    - Dev frontend → RENDER_FRONTEND_DEV_HOOK
    - Prod frontend → RENDER_FRONTEND_PROD_HOOK

4) Add the Deploy Hook URLs as GitHub repository secrets
- GitHub → Your repository → Settings → Secrets and variables → Actions → New repository secret
- Create these four secrets, pasting each corresponding Deploy Hook URL:
  - RENDER_BACKEND_DEV_HOOK
  - RENDER_BACKEND_PROD_HOOK
  - RENDER_FRONTEND_DEV_HOOK
  - RENDER_FRONTEND_PROD_HOOK
Why repository secrets?
- Our workflows in .github/workflows/backend-deploy.yml and frontend-deploy.yml read secrets.RENDER_* names. Repository-level secrets are simplest and work for both branches. If you prefer environment-scoped secrets, you can adapt workflows to use environments and environment secrets.

5) Verify CI/CD wiring
- Push a commit to the dev branch:
  - GitHub Actions should run the Frontend Deploy and/or Backend Deploy workflows for dev
  - The deploy steps call ops/*/deploy-dev.sh which POST the RENDER_*_DEV_HOOK URLs
  - On Render, you should see new builds triggered for the Dev services
- Push a commit to the main branch:
  - Same flow for PROD, using the RENDER_*_PROD_HOOK secrets

6) Functional check in the browser
- Open the Dev frontend URL (Render → password-generator-frontend-dev → Open)
  - The footer in the app shows the Backend API base. It should display your Dev backend URL
  - Click Generate and confirm a password appears
- Open the Prod frontend URL and repeat

Troubleshooting
- Frontend can’t reach backend (CORS or 403):
  - Ensure backend is healthy at https://<backend> /health
  - Confirm the correct VITE_API_BASE_URL_DEV/PROD is set on the respective frontend service and that the frontend was redeployed after setting env vars
  - Optionally restrict CORS on backend with CORS_ALLOW_ALL=false and set CORS_ORIGINS to the frontend’s domain
- Deploy workflows don’t trigger Render:
  - Check that the appropriate branch was pushed (dev or main)
  - Confirm all four GitHub secrets are present and not empty
  - In Render, verify that Deploy Hooks are enabled and the URL hasn’t been regenerated since adding it to GitHub
- Wrong API base displayed in UI:
  - Remember the precedence: PROD → DEV → default → localhost
  - If both VITE_API_BASE_URL_PROD and VITE_API_BASE_URL_DEV are set on the same site, the PROD one wins in the app UI
- Error: "URL constructor: https://<backend-dev-host>/api/v1/password is not a valid URL":
  - Cause: a placeholder like https://<backend-dev-host> was baked into the frontend env and is not a valid absolute URL.
  - Fix on Render: set VITE_API_BASE_URL_DEV (Dev site) or VITE_API_BASE_URL_PROD (Prod site) to the actual backend public URL (e.g., https://password-generator-backend-dev.onrender.com) and redeploy the frontend.
  - Local fallback: the app now validates the configured URL and will fall back to http://localhost:5000 in dev or window.origin in prod to avoid crashes; still set the correct env to enable API calls.

Where these values are used in this repo
- Frontend resolves the API base in src/App.vue and src/components/PasswordGenerator.vue
- Example env docs are in frontend/.env.example
- Deploy workflows use these secrets:
  - .github/workflows/backend-deploy.yml → RENDER_BACKEND_DEV_HOOK, RENDER_BACKEND_PROD_HOOK
  - .github/workflows/frontend-deploy.yml → RENDER_FRONTEND_DEV_HOOK, RENDER_FRONTEND_PROD_HOOK
- Bash deploy scripts read the same env vars (ops/backend/deploy-*.sh, ops/frontend/deploy-*.sh)


---

### CI/CD pipeline stages (staged view)

Both backend and frontend pipelines are now organized into clear, sequential stages so you can see progress step by step in GitHub Actions.

Backend Pipeline (on push/PR; deploy runs only on push to dev/main):
1) Build
   - Runs `bash ops/backend/build.sh`
   - Installs Python deps and byte-compiles sources to catch syntax errors.
2) Unit Tests
   - Runs `bash ops/backend/test.sh` (pytest on Python 3.14)
3) Functional Tests (simulation)
   - Runs `bash ops/backend/test-functional-sim.sh`
   - Default duration: `DURATION=60` seconds (override via job env)
4) Performance Tests (simulation)
   - Runs `bash ops/backend/test-performance-sim.sh`
   - Default: `DURATION=60`, `BATCH_SIZE=10` (override via job env)
5) Smoke Tests
   - Runs `bash ops/backend/smoke.sh` (starts Gunicorn, checks `/health` and `/api/v1/password`)
6) Deploy (Render)
   - On push to `dev`: uses `RENDER_BACKEND_DEV_HOOK`
   - On push to `main`: uses `RENDER_BACKEND_PROD_HOOK`

Frontend Pipeline (on push/PR; deploy runs only on push to dev/main):
1) Build
   - Runs `bash ops/frontend/build.sh` (`npm ci` + `npm run build`)
2) Functional Tests (simulation)
   - Runs `bash ops/frontend/test-functional-sim.sh`
   - Default: `DURATION=60`, `SLEEP_MS=100`
3) Performance Tests (simulation)
   - Runs `bash ops/frontend/test-performance-sim.sh`
   - Default: `DURATION=60`, `BATCH_SIZE=10`
4) Smoke Tests
   - Runs `bash ops/frontend/smoke.sh` (build + preview + HTTP check)
5) Deploy (Render)
   - On push to `dev`: uses `RENDER_FRONTEND_DEV_HOOK`
   - On push to `main`: uses `RENDER_FRONTEND_PROD_HOOK`

Manual deploy workflows (optional):
- `Frontend Deploy (manual)` and `Backend Deploy (manual)` can be triggered from the Actions tab via `workflow_dispatch` with an `environment` input (`dev` or `prod`). They call the same hook scripts under `ops/`.

Tuning simulations:
- You can override duration/parameters by editing the job env in the workflows or by running scripts locally, e.g.:
  - `DURATION=30 SLEEP_MS=50 bash ops/backend/test-functional-sim.sh`
  - `DURATION=45 BATCH_SIZE=20 bash ops/backend/test-performance-sim.sh`

Where to find logs:
- GitHub → Actions → pick the workflow run → select the current stage job (Build, Unit Tests, Functional, Performance, Smoke, Deploy) → expand steps to view logs.

Project structure additions:
- Added `ops/backend/build.sh` and `ops/frontend/build.sh` used by the Build stages.
