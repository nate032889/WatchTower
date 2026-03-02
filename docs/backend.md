# WatchTower Backend (Django) Documentation

The `backend` microservice is the central API and business logic hub for the WatchTower platform. It's built using Django and Django Rest Framework (DRF), backed by PostgreSQL, and uses Redis for inter-service communication.

## 1. Project Structure

```
backend/
├── api/                      # Django App: Core API logic
│   ├── migrations/           # Database migrations
│   ├── management/           # Custom Django management commands
│   ├── serializers/          # DRF Serializers for API validation/serialization
│   │   ├── interactor.py     # Serializer for incoming messages from fleet_manager
│   │   ├── integrations.py   # Serializers for BotIntegration (public & internal)
│   │   ├── organizations.py  # Serializer for Organization model
│   │   └── provider_credentials.py # Serializer for ProviderCredential model
│   ├── services/             # Core business logic (Service Layer)
│   │   ├── interactor_service.py # Handles incoming messages, LLM calls, attachments
│   │   └── intake_validation_service.py # Validates incoming data (e.g., controlled vocabulary)
│   ├── infrastructure/       # External client integrations (Infrastructure Layer)
│   │   ├── intake_client.py  # Client for Go intake_service
│   │   └── redis_publisher.py # Client for publishing to Redis
│   ├── v1/                   # API Version 1 endpoints (Delivery Layer)
│   │   ├── __init__.py
│   │   ├── interactor.py     # ViewSet for stateless bot messages
│   │   ├── integrations.py   # ViewSet for BotIntegration CRUD
│   │   ├── internal.py       # ViewSet for internal bot sync (exposes tokens)
│   │   ├── metadata.py       # API root metadata
│   │   ├── organizations.py  # ViewSet for Organization CRUD
│   │   ├── prompt.py         # ViewSet for direct LLM prompting (legacy/internal)
│   │   └── provider_credentials.py # ViewSet for ProviderCredential CRUD
│   ├── urls/                 # API URL configurations
│   │   └── v1.py             # URL patterns for API v1
│   ├── admin.py              # Django Admin configurations
│   ├── apps.py               # Django App configuration
│   └── models.py             # Django ORM models (Domain Layer)
├── agents/                   # Django App: LLM Agent implementations
│   ├── base.py               # Base abstract class for LLM agents
│   ├── gemini.py             # Google Gemini LLM agent implementation
│   ├── types.py              # Common types (LLMProvider, ServiceResult)
│   └── system_prompt.md      # Default system prompt for LLMs
├── watchtower/               # Django Project configuration
│   ├── settings.py           # Django settings (environment-aware)
│   ├── urls.py               # Project-level URL patterns
│   └── wsgi.py               # WSGI config
├── manage.py                 # Django management utility
├── Dockerfile                # Docker build instructions for the backend
├── requirements.txt          # Python dependencies
└── .env.local                # Local environment variables for native development
```

## 2. Key Components & Responsibilities

### 2.1. `api/models.py` (Domain Layer)

Defines the core data structures and relationships for the WatchTower platform.

*   **`Organization`**: Represents a multi-tenant entity. All other models are linked to an organization.
    *   `name` (unique), `created_at`.
*   **`ApiKey`**: Generic API keys (currently unused, but available).
*   **`ProviderCredential`**: Stores LLM API keys (e.g., Gemini, OpenAI) for a specific `Organization`.
    *   `organization` (ForeignKey), `provider` (Choices), `api_key` (encrypted in production), `is_active`.
*   **`Occurrence`**: Represents an active operational event (incident, pentest, CTF).
    *   `organization` (ForeignKey), `label` (unique), `domain`, `workflow`, `status`.
*   **`Evidence`**: Raw or parsed data related to an `Occurrence`.
    *   `occurrence` (ForeignKey), `content` (extracted text), `source_type` (e.g., `pcap`, `text`), `object_reference` (Minio key).
*   **`Conversation`**: Represents a unique chat thread/channel on a platform.
    *   `occurrence` (ForeignKey, optional), `platform_channel_id` (unique).
*   **`Message`**: A single turn in a `Conversation`.
    *   `conversation` (ForeignKey), `role` (user/model/system), `content`, `created_at`.
*   **`BotIntegration`**: Stores credentials for chat platform bots (e.g., Discord bot tokens).
    *   `organization` (ForeignKey), `platform` (Choices), `bot_token` (encrypted in production), `is_active`.
    *   **Django Signals:** `post_save` and `post_delete` signals on this model publish `start` or `stop` commands to Redis, orchestrating the `fleet_manager`.

### 2.2. `api/serializers/` (Serialization & Validation)

Uses Django Rest Framework `serializers.Serializer` and `serializers.ModelSerializer` for API input validation and output formatting.

*   **`interactor.py`**: `IncomingMessageSerializer` validates payloads from the `fleet_manager`.
*   **`integrations.py`**:
    *   `BotIntegrationSerializer`: For public CRUD operations (hides `bot_token` on read).
    *   `BotIntegrationSyncSerializer`: For internal `fleet_manager` sync (exposes `bot_token`).
*   **`organizations.py`**: `OrganizationSerializer` for `Organization` model.
*   **`provider_credentials.py`**: `ProviderCredentialSerializer` for `ProviderCredential` model (hides `api_key` on read).
*   **`prompt.py`**: `PromptSerializer` for direct LLM prompting (legacy/internal).

### 2.3. `api/v1/` (Delivery Layer - API Endpoints)

DRF `viewsets.ViewSet` and `viewsets.ModelViewSet` define the API endpoints. They are thin, delegating business logic to the `services` layer.

*   **`interactor.py`**: `InteractorViewSet` handles `POST /v1/interactor/message/` from stateless bots.
*   **`integrations.py`**: `BotIntegrationViewSet` for CRUD on `BotIntegration`s.
*   **`internal.py`**: `BotIntegrationSyncViewSet` (read-only) for `fleet_manager` to get active bot tokens.
*   **`organizations.py`**: `OrganizationViewSet` for CRUD on `Organization`s.
*   **`provider_credentials.py`**: `ProviderCredentialViewSet` for CRUD on `ProviderCredential`s.
*   **`prompt.py`**: `PromptViewSet` for direct LLM interaction.

### 2.4. `api/services/` (Service Layer - Business Logic)

Contains the core business logic, orchestrating interactions between models, infrastructure, and agents.

*   **`interactor_service.py`**: `InteractorService` is the heart of bot message processing.
    *   `process_incoming_message(payload)`: Main entry point.
    *   `_get_or_create_conversation()`: Ensures a `Conversation` exists for the channel.
    *   `_process_attachments()`: Handles attachment URLs (downloads, sends to `intake_service`, saves `Evidence`, auto-creates `Occurrence` if needed).
    *   `_get_llm_credentials()`: Fetches `ProviderCredential` for the `Organization`.
    *   Orchestrates LLM call (`agents` app) and saves `Message` history.
*   **`intake_validation_service.py`**: `IntakeValidationService` enforces controlled vocabulary and safety rules for incoming data.

### 2.5. `api/infrastructure/` (Infrastructure Layer - External Clients)

Abstracts external service integrations. Uses "Go-style error handling" (returns `(data, err)` tuples).

*   **`intake_client.py`**: `IntakeServiceClient` communicates with the Go `intake_service` for attachment processing.
*   **`redis_publisher.py`**: `publish_bot_command()` publishes messages to Redis for `fleet_manager` orchestration.

### 2.6. `agents/` (LLM Agent Implementations)

Encapsulates logic for interacting with various LLM providers.

*   **`base.py`**: `BaseLLMAgent` (abstract base class) defines the interface for all LLM agents.
*   **`gemini.py`**: `GeminiAgent` implements the `BaseLLMAgent` for Google Gemini.
    *   Handles API key injection, system prompt configuration, and history formatting.
*   **`agent.py`**: `get_llm_agent()` is a factory function to instantiate the correct LLM agent based on `LLMProvider`.
*   **`types.py`**: Defines `LLMProvider` enum and `ServiceResult` dataclass.
*   **`system_prompt.md`**: The default system prompt used to instruct the LLM.

### 2.7. `watchtower/settings.py`

The main Django settings file. It's configured to be environment-aware:

*   Prioritizes `.env.local` for native local development.
*   Falls back to `.env` for base settings (e.g., Docker Compose).
*   Uses `DOCKER_ENV=true` to switch between SQLite (local) and PostgreSQL (Docker) database configurations.

## 3. Development & Deployment Notes

*   **Migrations:** After any model changes, run `python manage.py makemigrations api` and `python manage.py migrate`.
*   **Secrets:** `api_key` and `bot_token` fields in models should be encrypted in a production environment. For development, they are stored as plain text.
*   **Authentication:** The API currently lacks robust user authentication beyond the Django Admin. Frontend mock login is for UI development only.
*   **Permissions:** ViewSets currently lack fine-grained permissions, exposing all data. This needs to be implemented for production.
