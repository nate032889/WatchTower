# WatchTower

WatchTower is a Django-based application that provides a unified interface to various Large Language Model (LLM) providers.

## Architecture

The application follows a service-oriented architecture with a clear separation of concerns:

- **Views (`web/views.py`, `api/v1/prompt.py`):** Handle incoming HTTP requests and outgoing responses. They are responsible for routing requests to the appropriate service and returning the service's response.
- **Services (`api/services/`):** Contain the core business logic of the application. They are responsible for processing requests, interacting with external services (like LLM providers), and returning results to the views.
- **Serializers (`api/serializers/`):** Used within the service layer to validate and deserialize request data.
- **Agents (`agents/`):** Provide a standardized interface for interacting with different LLM providers.

For more detailed architectural guidelines, please see the `guidelines/` directory.

## Documentation

Project documentation can be found in the `docs/` directory.

## REST API

### Prompt Endpoint

- **URL:** `/v1/prompt/`
- **Method:** `POST`
- **Description:** Submits a prompt to the specified LLM provider and returns the generated response. This endpoint is designed for conversational context, allowing you to pass the chat history with each request.

#### Request Body

```json
{
  "prompt": "Your new prompt text here",
  "provider": "gemini",
  "history": [
    {
      "role": "user",
      "parts": ["Hello!"]
    },
    {
      "role": "model",
      "parts": ["Hi there! How can I help you today?"]
    }
  ]
}
```

- `prompt` (string, required): The new text prompt to send to the LLM.
- `provider` (string, optional): The LLM provider to use. Defaults to `gemini`.
- `history` (array, optional): A list of previous conversation turns. Each item in the list must contain a `role` (`user` or `model`) and `parts` (a list of strings). The client is responsible for maintaining this history.

#### Success Response

- **Status Code:** `200 OK`

```json
{
  "response": "The LLM's generated response."
}
```

#### Error Responses

- **Status Code:** `400 Bad Request` (for invalid request data)
- **Status Code:** `502 Bad Gateway` (for upstream API failures)

```json
{
  "error": "A description of the error."
}
```
