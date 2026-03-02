# WatchTower Fleet Manager Documentation

The `fleet_manager` is a Python `asyncio` microservice responsible for dynamically managing the lifecycle of stateless chat bot instances (e.g., Discord bots). It acts as the delivery layer for chat platforms, forwarding messages to the central `backend` API and delivering responses back to the users.

## 1. Project Structure

```
fleet_manager/
├── config.py                 # Configuration loading and management
├── delivery/                 # Delivery Layer: Platform-specific bot clients
│   └── discord_bot.py        # StatelessDiscordBot (inherits discord.Client)
├── infrastructure/           # Infrastructure Layer: External API clients
│   └── api_client.py         # WatchTowerApiClient (communicates with backend API)
├── service/                  # Service Layer: Business logic for message processing
│   └── message_service.py    # MessageService (orchestrates API calls)
├── main.py                   # Application Entrypoint: Orchestrates layers, Redis listener, BotFleet manager
├── Dockerfile                # Docker build instructions
├── requirements.txt          # Python dependencies
└── .env.local                # Local environment variables for native development
```

## 2. Core Principles

*   **Statelessness:** The `fleet_manager` itself holds no persistent state about conversations, users, or LLM logic. All such state is managed by the central `backend` API.
*   **Event-Driven:** It reacts to commands received via Redis Pub/Sub to start or stop bot instances.
*   **Layered Architecture:** Strictly adheres to the Universal Microservice Layering Mandate (Delivery -> Service -> Infrastructure).
*   **Resilience:** Designed to handle bot login failures gracefully and to resync its state with the `backend` on startup.

## 3. Key Components & Responsibilities

### 3.1. `config.py`

*   **`load_env_file()`:** Handles loading environment variables with a clear hierarchy: `.env.local` (exclusive for local dev) or `.env` (fallback).
*   **`Config` class:** A centralized object holding all runtime configuration (API endpoints, Redis URL, etc.), making it easy to pass settings through the application.

### 3.2. `infrastructure/api_client.py`

*   **`WatchTowerApiClient`:** An infrastructure client that encapsulates all `aiohttp` logic for communicating with the main `backend` API.
*   **`send_message(payload)`:** Sends a message payload to the `backend`'s `/v1/interactor/message/` endpoint.
*   **Go-Style Error Handling:** Returns `(response_data, error)` tuples, never raises HTTP-specific exceptions.

### 3.3. `service/message_service.py`

*   **`MessageService`:** The service layer for processing incoming messages from Discord.
*   **`process_discord_message(...)`:**
    *   Constructs the standard payload for the `backend` API (including `platform`, `organization_id`, `channel_id`, `user_id`, `content`, `attachment_urls`).
    *   Calls `WatchTowerApiClient.send_message()` to forward the payload to the `backend`.
    *   Handles the `(response_data, error)` tuple from the infrastructure client, logs errors, and returns a user-friendly error message or the LLM's response.

### 3.4. `delivery/discord_bot.py`

*   **`StatelessDiscordBot` (inherits `discord.Client`):** The delivery layer for Discord.
*   **`on_ready()`:** Logs when the bot successfully connects to Discord.
*   **`on_message(message)`:**
    *   Contains **delivery-specific logic**: Ignores messages from itself, checks for mentions, strips the bot's mention from the message content.
    *   Extracts `channel_id`, `author_id`, `content`, and `attachment_urls`.
    *   Delegates all **business logic** to `MessageService.process_discord_message()`.
    *   **`send_in_chunks()`:** A helper method to correctly send long responses from the `backend` back to Discord, respecting Discord's message limits and `[SPLIT]` markers.
*   **`start_bot()`:** Starts the `discord.Client` connection, includes robust error handling for `discord.errors.LoginFailure` (e.g., invalid tokens).

### 3.5. `main.py` (Entrypoint)

*   **`BotFleet` class:** Manages the lifecycle of multiple `StatelessDiscordBot` instances.
    *   `start_bot(token, organization_id)`: Instantiates `WatchTowerApiClient`, `MessageService`, and `StatelessDiscordBot`, then creates an `asyncio.Task` to run the bot.
    *   `stop_bot(token)`: Cancels the `asyncio.Task` associated with a bot token.
*   **`sync_initial_state(fleet)`:**
    *   Executed on `fleet_manager` startup.
    *   Makes an HTTP GET request to the `backend`'s internal endpoint (`/v1/internal/bot-integrations/`) to fetch all currently active `BotIntegration`s.
    *   Calls `fleet.start_bot()` for each active integration, ensuring the `fleet_manager`'s state is synchronized with the database.
*   **`redis_listener(fleet)`:**
    *   Connects to Redis Pub/Sub (`redis.asyncio`).
    *   Subscribes to the `bot_integrations` channel.
    *   Listens for JSON messages with `action` (`start` or `stop`), `bot_token`, and `organization_id`.
    *   Calls `fleet.start_bot()` or `fleet.stop_bot()` based on the received command.
*   **`main()` function:** The main `asyncio` event loop.
    *   Loads configuration using `load_config()`.
    *   Performs `sync_initial_state()`.
    *   Starts the `redis_listener()` as a background task.

## 4. Environment Variables

The `fleet_manager` relies on the following environment variables, loaded via `config.py`:

*   `API_ENDPOINT`: URL for the `backend`'s interactor message endpoint (e.g., `http://api:8000/api/v1/interactor/message/` or `http://localhost:8000/api/v1/interactor/message/`).
*   `API_BOT_INTEGRATIONS_URL`: URL for the `backend`'s internal bot integrations endpoint (e.g., `http://api:8000/v1/internal/bot-integrations/` or `http://localhost:8000/v1/internal/bot-integrations/`).
*   `REDIS_URL`: Connection string for Redis (e.g., `redis://redis:6379` or `redis://localhost:6379`).
*   `DISCORD_MESSAGE_LIMIT`: (Optional) Max characters per Discord message chunk (default: 2000).

## 5. Development Workflow

1.  **Start Docker Infrastructure:** `docker-compose -f docker-compose.local.yml up -d` (ensures Redis is running).
2.  **Start Backend API:** Run the Django `backend` natively (e.g., `python manage.py runserver`).
3.  **Navigate to `fleet_manager/` directory.**
4.  **Install dependencies:** `pip install -r requirements.txt`
5.  **Create `.env.local`:** Ensure `API_ENDPOINT`, `API_BOT_INTEGRATIONS_URL`, and `REDIS_URL` point to `localhost`.
6.  **Run the service:** `python main.py`
