# WatchTower Intake Service (Go) Documentation

The `intake_service` is a Go microservice that functions as an ETL (Extract, Transform, Load) pipeline for processing file attachments. It accepts raw file uploads, stores them in Minio, parses their content based on file type, and returns the extracted, LLM-ready text.

## 1. Project Structure

```
intake_service/
├── config.go                 # Configuration loading and management
├── data/                     # Data Layer: Minio repository
│   └── minio.go              # Minio client for object storage operations
├── handlers/                 # Delivery Layer: HTTP request handlers
│   └── intake.go             # Handlers for /v1/intake, /v1/evidence, /v1/health
├── service/                  # Service Layer: Business logic for intake processing
│   ├── intake.go             # IntakeService orchestrates data and parsing
│   └── parser/               # File parsing implementations
│       ├── interface.go      # Defines the Parser interface
│       ├── factory.go        # Selects the correct parser based on file extension
│       ├── binary_parser.go  # Parses executable/binary files
│       ├── office_parser.go  # Parses .docx and .pptx files
│       ├── pcap_parser.go    # Parses .pcap network capture files
│       ├── pdf_parser.go     # Parses .pdf documents
│       └── text_parser.go    # Parses .txt, .md, .json files
├── main.go                   # Application Entrypoint: Orchestrates layers, HTTP server
├── routes.go                 # Defines HTTP routes and middleware
├── go.mod                    # Go module definition and dependencies
├── Dockerfile                # Docker build instructions
└── .env.local                # Local environment variables for native development
```

## 2. Core Principles

*   **ETL Pipeline:** Designed to efficiently ingest, process, and store various types of unstructured data from attachments.
*   **Microservice Isolation:** Completely decoupled from the `backend`'s business logic, focusing solely on file processing.
*   **Extensible Parsing:** The `parser` package is designed to easily add support for new file types.
*   **Layered Architecture:** Strictly adheres to the Universal Microservice Layering Mandate (Delivery -> Service -> Infrastructure -> Data).
*   **Configuration Management:** Uses a centralized `Config` object loaded from environment variables, with `.env` file support.

## 3. Key Components & Responsibilities

### 3.1. `config.go`

*   **`LoadConfig()`:** Handles loading environment variables with a clear hierarchy: `.env.local` (exclusive for local dev) or `.env` (fallback).
*   **`Config` struct:** A centralized object holding all runtime configuration (Minio credentials, server port).

### 3.2. `data/minio.go`

*   **`MinioRepository` interface:** Defines methods for interacting with Minio (`GetObject`, `SaveObject`).
*   **`minioRepository` struct:** Implements the `MinioRepository` interface using the `minio-go` SDK.
*   **`NewMinioRepository()`:** Constructor that takes configuration parameters (endpoint, keys, bucket) directly, making dependencies explicit.

### 3.3. `service/intake.go`

*   **`IntakeService` interface:** Defines the business logic for intake processing (`GetEvidence`, `ProcessIntake`).
*   **`intakeService` struct:** Implements the `IntakeService` interface.
*   **`ProcessIntake(ctx, filename, fileData, contentType)`:**
    *   Generates a UUID-based `objectKey`.
    *   Calls `MinioRepository.SaveObject()` to store the raw file.
    *   Uses `parser.GetParser()` to select the appropriate parser.
    *   Calls `Parser.Parse()` to extract text from the file data.
    *   Returns the `objectKey` and `extractedText`.
*   **`GetEvidence(ctx, objectKey)`:** Retrieves a file from Minio and parses it.

### 3.4. `service/parser/`

This package defines the parsing pipeline.

*   **`interface.go`**: Defines the `Parser` interface with a single `Parse(data []byte) (string, error)` method.
*   **`factory.go`**: `GetParser(filename string)` function returns the correct `Parser` implementation based on the file extension.
*   **Specific Parsers (`binary_parser.go`, `office_parser.go`, `pcap_parser.go`, `pdf_parser.go`, `text_parser.go`):**
    *   Each implements the `Parser` interface.
    *   They use libraries like `gopacket`, `ledongthuc/pdf`, `archive/zip`, `debug/elf`, `debug/pe` to extract human-readable text or summaries from various file types.
    *   For binary files, it extracts SHA256, format, imported libraries/functions, and printable strings.
    *   For PCAP files, it summarizes network flows (5-tuple, size).

### 3.5. `handlers/intake.go`

*   **`IntakeHandler`:** Contains HTTP handler functions.
*   **`HealthCheck(w, r)`:** `GET /v1/health` endpoint for service status.
*   **`GetEvidence(w, r)`:** `GET /v1/evidence/{object_key}` endpoint to retrieve and parse an object from Minio.
*   **`IntakeFile(w, r)`:** `POST /v1/intake` endpoint.
    *   Accepts `multipart/form-data` file uploads.
    *   Delegates file processing to `IntakeService.ProcessIntake()`.
    *   Returns JSON with `object_key` and `extracted_text`.

### 3.6. `routes.go`

*   **`NewRouter(svc service.IntakeService)`:** Configures the `chi` router, middleware, and registers all HTTP routes under the `/v1` prefix.

### 3.7. `main.go` (Entrypoint)

*   Loads configuration using `config.LoadConfig()`.
*   Initializes `MinioRepository` with the loaded configuration.
*   Initializes `IntakeService` with the repository.
*   Sets up the HTTP router using `NewRouter()`.
*   Starts the HTTP server on the configured port.

## 4. Environment Variables

The `intake_service` relies on the following environment variables, loaded via `config.go`:

*   `MINIO_ENDPOINT`: Minio server address (e.g., `minio:9000` or `localhost:9000`).
*   `MINIO_ACCESS_KEY`: Minio access key.
*   `MINIO_SECRET_KEY`: Minio secret key.
*   `MINIO_BUCKET_NAME`: The bucket to use for storing evidence (e.g., `evidence`).
*   `SERVER_PORT`: The port the service should listen on (default: `3000`).

## 5. Development Workflow

1.  **Start Docker Infrastructure:** `docker-compose -f docker-compose.local.yml up -d` (ensures Minio is running).
2.  **Navigate to `intake_service/` directory.**
3.  **Install dependencies:** `go mod tidy`
4.  **Create `.env.local`:** Ensure `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `MINIO_BUCKET_NAME` point to `localhost` and `miniopassword`.
5.  **Run the service:** `go run main.go`
6.  Access the service at `http://localhost:3000`.
