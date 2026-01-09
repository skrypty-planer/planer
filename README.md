### Bugdet Planner (Flask backend + Vue frontend)

Budget Planner – Full-stack Web Application
Full-stackowa aplikacja webowa typu planer budżetu, umożliwiająca użytkownikom zarządzanie finansami osobistymi: rejestrowanie transakcji, analizę wydatków oraz wizualizację danych finansowych.
 Projekt został zrealizowany w architekturze klient–serwer z wykorzystaniem Python Flask (backend) oraz Vue 3 + Vite + TypeScript (frontend), wraz z pełnym pipeline’em CI/CD.
Architektura projektu
- Backend: Flask (Python), architektura warstwowa, wzorce projektowe (Singleton, Managerowie)
- Frontend: Vue 3, Vite, TypeScript, komponenty SPA
- CI/CD: GitHub Actions (testy, build, smoke)
- CD / Hosting: Render (deploy hooks + render.yaml)


Testy: pytest (backend)
---
ops/
  backend/
    deploy.sh
    smoke.sh
    start.sh
    test.sh
  frontend/
    deploy.sh
    smoke.sh

backend/
  src/
    error_handling/
      exception.py
      logger.py
    models/
      transaction.py
      user.py
    routes/
      auth.py
      health.py
      transactions.py
    utilities/
      AuthManager.py
      CacheManager.py
      Singleton.py
      TransactionManager.py
      global_utils.py
    __init__.py
    app.py
    config.py
  tests/
    test_auth.py
    test_auth_manager.py
    test_cache.py
    test_cache_manager.py
    test_factory.py
    test_flask_importer.py
    test_global_utils.py
    test_transaction_manager.py
  requirements.txt
  pyproject.toml
  pytest.ini

frontend/
  public/
  src/
    components/
      AppHeader.vue
      AppFooter.vue
      MenuNav.vue
      Modal.vue
      PieChart.vue
      TransactionFormModal.vue
      EditProfileModal.vue
      EmptyState.vue
    pages/
      Home.vue
      Login.vue
      Register.vue
      Transactions.vue
      Analytics.vue
    services/
      api.ts
      auth.ts
    styles/
      main.css
    App.vue
    main.ts
    router.ts
  index.html
  package.json
  vite.config.js
  tsconfig.json
  .env.example

.github/workflows/
  backend-ci.yaml
  backend-deploy.yaml
  frontend-ci.yaml
  frontend-deploy.yaml

render.yaml
README.md

### Backend (Flask)
Główne elementy
 -Routes:
  -/auth – logowanie i rejestracja
  -/transactions – CRUD transakcji
  -/health – health-check
 -Models: User, Transaction
 -Utilities:
 -Singleton – implementacja wzorca Singleton
 -AuthManager – logika autoryzacji
 -TransactionManager – logika biznesowa transakcji
 -CacheManager – cache aplikacyjny
 -Error handling – centralna obsługa wyjątków i logowania
 
Uruchomienie lokalne
```
cd backend
pip install -r requirements.txt
python src/app.py
```
---
### Frontend (Vue 3 + Vite)
Funkcjonalności
 -logowanie / rejestracja
 -lista transakcji
 -dodawanie i edycja transakcji
 -analityka (wykresy)
 -SPA z routingiem

---
GitHub Actions (CI/CD)
W projekcie zastosowano GitHub Actions do realizacji procesów Continuous Integration (CI) oraz Continuous Deployment (CD).
 Pliki workflow znajdują się w katalogu .github/workflows/ i są podzielone na osobne pipeline’y dla backendu oraz frontendu.

 -backend-ci.yaml
  -Środowisko: Python 3.14
  -Uruchamia testy jednostkowe oraz testy typu smoke:
   -ops/backend/test.sh
   -ops/backend/smoke.sh
 -Pipeline weryfikuje poprawność logiki aplikacji backendowej planera budżetu przed wdrożeniem.
 -frontend-ci.yaml
  -Środowisko: Node.js 20
  -Uruchamia test typu smoke:
   -ops/frontend/smoke.sh
   -Sprawdza poprawność budowania aplikacji frontendowej (Vue 3).
-Continuous Deployment
 -backend-deploy.yaml oraz frontend-deploy.yaml


Uruchamiane automatycznie po wypchnięciu zmian do odpowiednich gałęzi:


dev – środowisko deweloperskie
main – środowisko produkcyjne
Workflow wywołuje odpowiednie skrypty:
ops/backend/deploy.sh
ops/frontend/deploy.sh
Skrypty te uruchamiają Render Deploy Hooks, inicjując proces wdrożenia aplikacji.

Sekrety repozytorium
Do obsługi automatycznego wdrażania wykorzystywane są sekrety GitHub, zawierające adresy webhooków Rendera:
Backend
RENDER_BACKEND_DEV_HOOK
RENDER_BACKEND_PROD_HOOK
Frontend
RENDER_FRONTEND_DEV_HOOK
RENDER_FRONTEND_PROD_HOOK
Sekrety te są konfigurowane w:
 GitHub → Settings → Secrets and variables → Actions.
Mapowanie gałęzi na środowiska
Gałąź dev → środowisko DEV
Gałąź main → środowisko PROD
Takie podejście zapewnia automatyczne testowanie oraz bezpieczne i powtarzalne wdrażanie aplikacji planera budżetu.

---
Render deployment
Option A — Render Blueprint (rekomendowane):
Plik: render.yaml zawiera definicje zarówno backendu (Web Service – Flask), jak i frontendu (Static Site – Vue 3).


W panelu Render należy utworzyć nowy Blueprint i wskazać repozytorium projektu.


Backend service:


Komenda budowania: instalacja zależności z pliku backend/requirements.txt


Komenda startowa: uruchomienie aplikacji Flask za pomocą serwera Gunicorn


Ścieżka health check: /health


Zmienne środowiskowe: zdefiniowane w render.yaml (konfiguracja aplikacji, ustawienia CORS itp.), możliwe do edycji w panelu Render


Frontend service (Static Site):


Komenda budowania: instalacja zależności oraz zbudowanie wersji produkcyjnej aplikacji Vue


Katalog publikacji: frontend/dist


Po wdrożeniu backendu należy ustawić zmienną VITE_API_BASE_URL wskazującą na publiczny adres backendu (np. https://budget-planner-backend.onrender.com)


Option B — Manual services:
Backend (Web Service):


Utworzenie nowej usługi typu Web Service z repozytorium projektu


Użycie tych samych komend budowania i uruchamiania co w opcji Blueprint


Konfiguracja ścieżki health check /health


Frontend (Static Site):


Utworzenie nowej usługi typu Static Site


Zbudowanie aplikacji frontendowej z katalogu frontend


Publikacja katalogu frontend/dist


Ustawienie zmiennej VITE_API_BASE_URL na publiczny adres backendu


After first deploy:
Wejście na publiczny adres frontendu


Rejestracja lub logowanie użytkownika


Sprawdzenie poprawności działania aplikacji planera budżetu poprzez:


pobranie listy transakcji,


dodanie nowej transakcji,


wyświetlenie podsumowań oraz widoków analitycznych


Prawidłowe wykonanie powyższych kroków potwierdza poprawną konfigurację oraz wdrożenie aplikacji planera budżetu.



---
### API usage examples
Pobranie podsumowania dashboardu dla użytkownika
curl 'http://localhost:5000/transactions/summary?user_id=123'

Pobranie ostatnich 5 transakcji
curl 'http://localhost:5000/transactions/recent?user_id=123'

Pobranie wszystkich transakcji z filtrowaniem
curl 'http://localhost:5000/transactions/get?user_id=123&dateFrom=2026-01-01&dateTo=2026-01-09&type=expense&category=Jedzenie'

Dodanie nowej transakcji
curl -X POST 'http://localhost:5000/transactions/store'
-H 'Content-Type: application/json'
-d '{"user_id":"123","name":"Lunch","amount":50,"date":"2026-01-09","type":"expense","category":"Jedzenie"}'

Aktualizacja transakcji
curl -X PUT 'http://localhost:5000/transactions/update/456'
-H 'Content-Type: application/json'
-d '{"amount":55}'

Usunięcie transakcji
curl -X DELETE 'http://localhost:5000/transactions/delete/456?user_id=123'

Pobranie podziału transakcji po kategoriach
curl 'http://localhost:5000/transactions/categories?user_id=123&type=expense&period=monthly'

makefile
Skopiuj kod
Responses:
{
"transactions": [
{ "id": "1", "name": "Lunch", "amount": 50, "date": "2026-01-09", "type": "expense", "category": "Jedzenie" },
{ "id": "2", "name": "Salary", "amount": 5000, "date": "2026-01-01", "type": "income", "category": "Pensja" }
]
}

{
"summary": {
"incomeDaily": 5000,
"expenseDaily": 50,
"balanceDaily": 4950,
"incomeMonthly": 5000,
"expenseMonthly": 50,
"balanceMonthly": 4950
}
}

{
"breakdown": [
{ "category": "Jedzenie", "amount": 200, "percentage": 40 },
{ "category": "Transport", "amount": 300, "percentage": 60 }
]
}

scss
Skopiuj kod
Errors (HTTP 400):
{ "error": "Invalid user_id, transaction ID, or filter parameters" }


---
### Notes
- **Singleton pattern** is implemented via a metaclass in `backend/src/utilities/Singleton.py`. All classes that require a single shared instance use this metaclass and expose access through `ClassName.get_instance()`.
- **Classes using Singleton in `src/utilities`:**
  - `AuthManager.py` – manages authentication logic, token validation, and user sessions.
  - `CacheManager.py` – handles in-memory caching of frequently accessed data (e.g., transaction summaries).
  - `TransactionManager.py` – centralizes transaction operations such as adding, updating, and deleting transactions while ensuring consistent state.
  - `Cache.py` – supports caching utilities and integration with `CacheManager`.
  - Any other class in `src/utilities` that needs a global shared instance follows the Singleton metaclass pattern.
- **Default CORS** allows all origins; to restrict, set `CORS_ALLOW_ALL=false` and specify allowed origins in `CORS_ORIGINS`.
- **Transaction endpoints** validate input strictly: amounts must be numbers, dates in `YYYY-MM-DD` format, and categories must match predefined lists.
- **Dashboard, charts, and category breakdown endpoints** provide aggregated data; filters can be applied via query parameters such as `dateFrom`, `dateTo`, `type`, and `category`.
- **CI smoke tests** rely on `curl` and `jq` (installed in the workflow) to check basic endpoint availability and correct JSON responses.



---
## Prerequisites
- Two environments on Render created from this repo (via `render.yaml` Blueprint or manual setup):
  - **Dev**: services named like `budget-planner-backend-dev` and `budget-planner-frontend-dev` on branch `dev`
  - **Prod**: services named like `budget-planner-backend-prod` and `budget-planner-frontend-prod` on branch `main`
- Branch mapping: `dev` → Dev environment, `main` → Prod environment
- Node.js (v18+) and npm/yarn installed for frontend
- Python 3.11+ with virtual environment for backend
- Required packages installed:
  - Backend: `pip install -r backend/requirements.txt`
  - Frontend: `npm install` or `yarn install` in `frontend/`
- Access to environment variables:
  - Backend: `.env` or Render environment variables for database, CORS, and other configs
  - Frontend: `.env` or `.env.local` with `VITE_API_BASE_URL` pointing to the backend
- Optional but recommended: `curl` and `jq` for running smoke tests locally
 used by the Build stages.
