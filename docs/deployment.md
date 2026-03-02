# WatchTower Deployment & Environment Configuration

This document details how to deploy and configure the WatchTower microservices, covering both full Docker Compose deployments and local development setups.

## 1. Environment Variable Strategy

WatchTower services are configured using environment variables. A consistent loading hierarchy is applied across all services:

1.  **`.env.local`**: (Highest precedence) Used exclusively for **local native development**. These files are typically `.gitignore`d and contain machine-specific settings (e.g., `localhost` URLs, personal API keys).
2.  **`.env`**: (Fallback) Used for **base development settings** or when `.env.local` is not present. Can be used for shared development configurations.
3.  **System Environment Variables**: (Lowest precedence) Used in **Docker Compose deployments** (where `.env` files are explicitly passed or variables are defined in `docker-compose.yml`) and production environments.

This hierarchy ensures that local overrides are easy, while containerized deployments remain consistent.

## 2. Docker Compose Deployments

### 2.1. Full Stack Deployment (`docker-compose.yml`)

This is the primary deployment method for a production-like environment, running all services in Docker containers.

*   **File:** `docker-compose.yml` (at project root)
*   **Services Included:** `db` (PostgreSQL), `redis`, `minio`, `api` (Django), `frontend` (Vue.js + NGINX), `fleet_manager` (Python), `intake_service` (Go).
*   **Networking:** Services communicate using Docker's internal DNS (e.g., `http://api:8000`).
*   **Persistence:** Uses Docker volumes for `postgres_data`, `redis_data`, and `minio_data`.

**Key Environment Variables (defined in `docker-compose.yml` or passed via `.env`):**

*   **`db` (PostgreSQL):**
    *   `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
*   **`minio`:**
    *   `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`
*   **`api` (Django):**
    *   `DOCKER_ENV=true`: Signals Django to use PostgreSQL.
    *   `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST=db`, `DB_PORT=5432`
    *   `REDIS_URL=redis://redis:6379/0`
    *   `INTAKE_SERVICE_URL=http://intake-service:3000/v1/intake`
    *   `GEMINI_API_KEY`: Your LLM API key.
*   **`fleet_manager` (Python):**
    *   `API_ENDPOINT=http://api:8000/api/v1/interactor/message/`
    *   `API_BOT_INTEGRATIONS_URL=http://api:8000/v1/internal/bot-integrations/`
    *   `REDIS_URL=redis://redis:6379/0`
    *   `DISCORD_BOT_TOKEN`: Your Discord bot token (should be passed via `.env`).
*   **`intake_service` (Go):**
    *   `MINIO_ENDPOINT=minio:9000`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `MINIO_BUCKET_NAME`
    *   `SERVER_PORT=3000`

**To Deploy:**

1.  Ensure your main `.env` files (e.g., `backend/.env`, `fleet_manager/.env`) are configured.
2.  Run `docker-compose up --build -d`.

### 2.2. Local Infrastructure Only (`docker-compose.local.yml`)

This Compose file is designed to run only the stateful infrastructure services (DB, Redis, Minio) in Docker, allowing application code to run natively on the host machine.

*   **File:** `docker-compose.local.yml` (at project root)
*   **Services Included:** `postgres`, `redis`, `minio`.
*   **Networking:** Ports are exposed to `localhost` (e.g., `5432:5432`).
*   **Persistence:** Uses local Docker volumes (`postgres_local_data`, `redis_local_data`, `minio_local_data`).

**Key Environment Variables (defined in `docker-compose.local.yml`):**

*   **`postgres`:** `POSTGRES_DB=watchtower_db`, `POSTGRES_USER=watchtower_user`, `POSTGRES_PASSWORD=watchtower_password`.
*   **`minio`:** `MINIO_ROOT_USER=minioadmin`, `MINIO_ROOT_PASSWORD=miniopassword`.

**To Start Local Infrastructure:**

1.  Run `docker-compose -f docker-compose.local.yml up -d`.

## 3. Native Local Development

When running application code natively, each service needs its own `.env.local` file to connect to the Dockerized infrastructure via `localhost`.

### 3.1. `backend/.env.local`

```ini
# Django Core
DJANGO_SECRET_KEY=local-insecure-secret-key-for-dev
DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL running in Docker)
DB_NAME=watchtower_db
DB_USER=watchtower_user
DB_PASSWORD=watchtower_password
DB_HOST=localhost
DB_PORT=5432

# Redis (Running in Docker)
REDIS_URL=redis://localhost:6379/0

# Service URLs (Go Intake Service running natively)
INTAKE_SERVICE_URL=http://localhost:3000/v1/intake

# LLM Provider API Keys (can be left empty if not used locally)
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3.2. `frontend/.env.local`

```ini
# These variables are used by vite.config.js for the dev server proxy
VITE_API_V1_URL=http://127.0.0.1:8000
VITE_API_INTAKE_URL=http://127.0.0.1:3000
```

### 3.3. `fleet_manager/.env.local`

```ini
# The central API endpoints, running natively on the host at port 8000
API_ENDPOINT=http://localhost:8000/api/v1/interactor/message/
API_BOT_INTEGRATIONS_URL=http://localhost:8000/v1/internal/bot-integrations/

# Redis, running in a local Docker container at port 6379
REDIS_URL=redis://localhost:6379/0
```

### 3.4. `intake_service/.env.local`

```ini
# Minio, running in Docker
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=miniopassword
MINIO_BUCKET_NAME=evidence

# Server Port
SERVER_PORT=3000
```
