# WatchTower Architecture Overview

WatchTower is designed as a modular, multi-tenant microservices platform. This document provides a high-level overview of the system's architecture, the responsibilities of each microservice, and how they communicate.

## 1. Core Principles

*   **Domain-Driven Design (DDD):** Business logic is isolated from infrastructure and delivery mechanisms.
*   **Separation of Concerns:** Each service has a clear, well-defined responsibility.
*   **Stateless Interactors:** Bot runners (like `fleet_manager`) are stateless, delegating all complex logic and state management to the central `backend` API.
*   **Event-Driven Orchestration:** Redis Pub/Sub is used for real-time communication between services, particularly for bot lifecycle management.
*   **API Gateway Pattern:** NGINX acts as an API Gateway, routing requests to the appropriate backend services based on subdomains.
*   **Layered Architecture:** Each microservice adheres to a strict layered architecture (Delivery -> Service -> Infrastructure -> Data) to maximize cohesion and minimize coupling.

## 2. Microservices Overview

The WatchTower ecosystem comprises the following key microservices:

### 2.1. `frontend` (Vue.js + NGINX)

*   **Technology:** Vue.js 3, Vuetify 3, Vite, NGINX.
*   **Responsibility:** Provides the user interface for managing organizations, LLM provider credentials, bot integrations, and system templates. NGINX serves the static files and acts as the API Gateway for all backend services.
*   **Communication:**
    *   Serves static assets directly.
    *   Proxies `api.watchtower.com` to the `backend` (Django API).
    *   Proxies `intake.watchtower.com` to the `intake_service` (Go ETL).

### 2.2. `backend` (Django + DRF)

*   **Technology:** Python, Django, Django Rest Framework, PostgreSQL, Redis.
*   **Responsibility:** The central brain of WatchTower.
    *   Manages core domain models: `Organization`, `Occurrence`, `Evidence`, `Conversation`, `Message`, `ProviderCredential`, `BotIntegration`.
    *   Provides RESTful APIs for the `frontend` and internal services.
    *   Contains the `InteractorService` for processing incoming messages from stateless bots (LLM orchestration, attachment processing, history management).
    *   Publishes bot lifecycle events to Redis.
*   **Communication:**
    *   **Inbound:** HTTP requests from `frontend` and `fleet_manager`.
    *   **Outbound:**
        *   Database: PostgreSQL (`db` service).
        *   Object Storage: Minio (`minio` service) via `intake_service`.
        *   LLM Providers: External APIs (e.g., Google Gemini).
        *   Redis: Publishes bot commands (`redis` service).
        *   Intake Service: HTTP requests to `intake_service` for attachment processing.

### 2.3. `fleet_manager` (Python asyncio)

*   **Technology:** Python, `asyncio`, `discord.py`, `aiohttp`, `redis.asyncio`.
*   **Responsibility:** A stateless, long-running runner for Discord bot instances.
    *   Listens to Redis Pub/Sub for `start` and `stop` commands for `BotIntegration`s.
    *   Dynamically instantiates and manages `discord.Client` instances.
    *   Forwards all incoming Discord messages (including attachments URLs) to the `backend` API.
    *   Receives responses from the `backend` and delivers them back to Discord.
*   **Communication:**
    *   **Inbound:** Redis Pub/Sub (`redis` service).
    *   **Outbound:**
        *   Discord API: WebSockets.
        *   Backend API: HTTP POST requests to `backend` (`api` service).
        *   Backend API: HTTP GET requests to `backend` for initial state sync.

### 2.4. `intake_service` (Go)

*   **Technology:** Go, `chi` router, `minio-go`, `gopacket`, `ledongthuc/pdf`, `archive/zip`.
*   **Responsibility:** An ETL (Extract, Transform, Load) pipeline for processing file attachments.
    *   Accepts multipart file uploads via HTTP POST.
    *   Generates unique object keys (UUIDs).
    *   Saves raw files to Minio.
    *   Parses file content based on type (text, PCAP, binary, PDF, DOCX, PPTX).
    *   Returns extracted, LLM-ready text and the Minio object key.
*   **Communication:**
    *   **Inbound:** HTTP POST requests from `backend`.
    *   **Outbound:**
        *   Object Storage: Minio (`minio` service).

### 2.5. `db` (PostgreSQL)

*   **Technology:** PostgreSQL.
*   **Responsibility:** Persistent storage for all application data, including `Organizations`, `Occurrences`, `Evidence`, `Conversations`, `Messages`, `ProviderCredentials`, and `BotIntegrations`.

### 2.6. `redis`

*   **Technology:** Redis.
*   **Responsibility:** In-memory data store primarily used for:
    *   **Pub/Sub:** Orchestrating bot lifecycle events between `backend` and `fleet_manager`.
    *   Potentially for caching or session management in the future.

### 2.7. `minio`

*   **Technology:** Minio (S3-compatible object storage).
*   **Responsibility:** Stores raw file attachments uploaded via the `intake_service`. These files are referenced by `object_reference` in the `Evidence` model.

## 3. Data Flow Examples

### 3.1. User Sends Message with Attachment in Discord

1.  **Discord User:** Sends a message with an attachment to a bot.
2.  **`fleet_manager`:** `StatelessDiscordBot.on_message` event fires.
    *   Parses message content and extracts `attachment_urls`.
    *   Constructs a payload including `organization_id`, `channel_id`, `user_id`, `content`, `attachment_urls`.
    *   Calls `message_service.process_discord_message`.
3.  **`fleet_manager` (`MessageService`):**
    *   Constructs the final payload.
    *   Calls `api_client.send_message`.
4.  **`backend` (Django API - `InteractorViewSet`):**
    *   Receives `POST /v1/interactor/message/`.
    *   Validates payload using `IncomingMessageSerializer`.
    *   Calls `InteractorService.process_incoming_message`.
5.  **`backend` (`InteractorService`):**
    *   `_get_or_create_conversation`: Finds/creates `Conversation` for `platform_channel_id`.
    *   `_process_attachments`:
        *   If `conversation.occurrence` is `None`, auto-creates a new `Occurrence` and links it.
        *   For each `attachment_url`:
            *   Downloads the file from the URL.
            *   Sends the file as multipart/form-data to `intake.watchtower.com/v1/intake`.
            *   Receives `object_key` and `extracted_text` from `intake_service`.
            *   Saves `Evidence` record linked to `Occurrence`.
            *   Prepends `extracted_text` to the user's `content` as `attachment_context`.
    *   Saves user's `Message` to DB.
    *   `_get_llm_credentials`: Retrieves `ProviderCredential` for the `organization_id`.
    *   Fetches `Message` history (excluding current user message).
    *   Calls `GeminiAgent.generate_response` with `attachment_context + content` and history.
    *   Saves LLM's response as a `Message` to DB.
    *   Returns LLM's response string.
6.  **`fleet_manager` (`MessageService`):** Receives LLM response.
7.  **`fleet_manager` (`StatelessDiscordBot`):** `send_in_chunks` delivers the response to Discord.
8.  **Discord User:** Sees the bot's response.

### 3.2. User Creates/Updates Bot Integration via Web UI

1.  **Frontend User:** Navigates to Settings, adds/edits a bot token, and clicks "Save".
2.  **Frontend (Vue.js):** `ProviderSettings.vue` calls `store.toggleBotStatus` or `store.createBotIntegration`.
3.  **Frontend (Pinia Store):** Sends `POST` or `PATCH` request to `api.watchtower.com/v1/bot-integrations/`.
4.  **`backend` (Django API - `BotIntegrationViewSet`):**
    *   Receives request, validates payload.
    *   Saves/updates `BotIntegration` record in PostgreSQL.
5.  **`backend` (Django Signals - `post_save`):**
    *   `handle_bot_integration_save` receiver is triggered.
    *   Calls `publish_bot_command` to Redis.
6.  **`backend` (`RedisPublisher`):** Publishes `{"action": "start", "bot_token": "...", "organization_id": ...}` (or "stop") to Redis channel `bot_integrations`.
7.  **`fleet_manager` (`redis_listener`):** Receives the command.
8.  **`fleet_manager` (`BotFleet`):**
    *   If "start": Calls `start_bot`, which instantiates `WatchTowerApiClient`, `MessageService`, and `StatelessDiscordBot`, then starts the `discord.Client` as an `asyncio.Task`.
    *   If "stop": Calls `stop_bot`, which cancels the corresponding `asyncio.Task`.
9.  **Discord:** The bot appears/disappears online.
