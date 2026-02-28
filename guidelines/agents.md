# Agents Library Guidelines

This document provides specific guidelines for the `agents` library, which is responsible for abstracting interactions with various Large Language Model (LLM) providers.

This document supplements the main [Architectural Guidelines](./ARCHITECTURAL_GUIDELINES.md).

## Core Principles

- **Standardized Interface:** Each agent must implement a common interface to ensure that the `PromptService` can interact with any provider in a consistent manner.
- **Provider-Specific Logic:** All logic specific to a particular LLM provider (e.g., API key handling, request formatting, error parsing) should be fully encapsulated within that provider's agent module.
- **Data Validation:** As per the architectural guidelines, all data transfer objects (DTOs) or configuration models used within the agents library must use `Pydantic` for strict data validation and clear schema definition.

## Agent Structure (Example)

An agent should consist of:
1.  A `Pydantic` model for its specific settings (if any).
2.  A class that implements the base agent interface.
3.  Error handling specific to that provider's SDK or API.
