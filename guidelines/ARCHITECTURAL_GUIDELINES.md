# Architectural Guidelines

This document outlines the architectural principles and guidelines for the WatchTower project.

## General Principles

- **Domain-Driven Design (DDD):** We follow DDD principles to model our software on the business domain. Core concepts and logic should be encapsulated within domain models.
- **Separation of Concerns:** Logic should be separated into appropriate layers (e.g., views, services, data access).
- **Keep Views Thin:** Views (or entry points like a bot) should be responsible for handling external interactions and routing requests to the service layer. They should not contain business logic.
- **Service Layer:** The service layer contains the core business logic of the application. It should be independent of the web framework or entry point.
- **Data Access:** All database interaction should be handled by a dedicated data access layer.

## Specific Guidelines

- **Serializers:** Serializers should be used in the service layer to validate and deserialize request data, and to serialize data for responses. They should not be used directly in views.
- **Data Structures:** For low-level libraries and data transfer objects (like those in the `agents` library), use `Pydantic` models over standard `dataclasses` to ensure robust data validation.
- **Control Flow:** Prefer using guard clauses (early exits) over nested if/else statements to reduce cognitive complexity and improve readability. Handle failure cases first.
- **Documentation:**
    - New components or modules should include a `README.md` file that describes their purpose, usage, and any relevant architectural decisions.
    - All function and method docstrings should follow this format:
      """
      A brief, one-line summary of the function's purpose.
      :param param_name: Description of the parameter.
      :return: Description of the return value.
      """

## Discord Bot Architecture

The `discord_bot` application follows a 3-tier architecture to ensure a clean separation of concerns:

1.  **Application Layer (`bot.py`):** This is the main entry point. It is responsible only for connecting to Discord, receiving events, and delegating all logic to the Service Layer.
2.  **Service Layer (`service/`):** Contains all business logic. This includes managing conversation context, triggering summarization, and constructing payloads for the WatchTower API.
3.  **Data Layer (`data/`):** Implements the Repository Pattern.
    - It is responsible for all database operations (CRUD).
    - It must use a **normalized relational schema**, not JSON blobs.
    - It must return **Pydantic models** as Data Transfer Objects (DTOs) to the service layer.
4.  **Logging:** All modules should use the centralized Python `logging` framework. Direct `print()` statements for logging purposes are forbidden.

## AI Assistant Guidelines

Before making decisions or changes, please reference this document. To provide new guidelines, such as for the `agents` library, create a corresponding markdown file (e.g., `guidelines/AGENTS.md`) and I will incorporate it.
