# WatchTower Frontend (Vue.js) Documentation

The `frontend` microservice provides the user interface for the WatchTower platform. It's built with Vue.js 3, styled with Vuetify 3, and uses Pinia for state management. NGINX serves the static assets and acts as an API Gateway.

## 1. Project Structure

```
frontend/
├── public/                 # Static assets (e.g., index.html, favicon)
├── src/                    # Vue.js application source code
│   ├── assets/             # Static assets (images, fonts, etc.)
│   ├── components/         # Reusable Vue components
│   │   ├── OrganizationManager.vue # Form to create new organizations
│   │   ├── OrganizationSelector.vue # Dropdown to select active organization
│   │   ├── ProviderSettings.vue    # Forms for LLM credentials and Bot Integrations
│   │   └── TemplateManager.vue     # Table and form for managing templates
│   ├── router/             # Vue Router configuration
│   │   └── index.js        # Defines routes and navigation guards
│   ├── stores/             # Pinia stores for global state management
│   │   └── app.js          # Main application store (auth, orgs, integrations, etc.)
│   ├── views/              # Top-level pages/views
│   │   ├── Dashboard.vue   # Displays status of integrations
│   │   ├── Login.vue       # Mock login page
│   │   ├── Settings.vue    # Page for managing organizations, credentials, integrations
│   │   └── Templates.vue   # Page for managing templates
│   ├── App.vue             # Main application layout and router view
│   └── main.js             # Vue application entry point (initializes Vue, Pinia, Vuetify, Router)
├── Dockerfile              # Multi-stage Dockerfile for building and serving the frontend
├── nginx.conf              # NGINX configuration for serving static files and API Gateway
├── package.json            # Node.js dependencies
├── vite.config.js          # Vite build configuration (includes dev server proxy)
└── .env.local              # Local environment variables for native frontend development
```

## 2. Key Technologies

*   **Vue.js 3 (Composition API):** Reactive frontend framework.
*   **Vuetify 3:** Material Design component framework for a consistent UI.
*   **Pinia:** Lightweight and intuitive state management library for Vue.js.
*   **Vue Router:** Handles client-side routing and navigation.
*   **Vite:** Fast build tool and development server.
*   **NGINX:** Serves static files in production and acts as an API Gateway for backend services.

## 3. Global State Management (`stores/app.js`)

The Pinia store (`useAppStore`) is central to managing the application's global state:

*   **Authentication:** `isAuthenticated`, `user`, `login()`, `logout()`. (Currently mocked).
*   **Organizations:** `activeOrganizationId`, `organizations`, `fetchOrganizations()`, `createOrganization()`, `setActiveOrganization()`.
*   **Provider Credentials:** `providerCredentials`, `fetchProviderCredentials()`, `deleteProviderCredential()`.
*   **Bot Integrations:** `botIntegrations`, `fetchBotIntegrations()`, `deleteBotIntegration()`, `toggleBotStatus()`.
*   **Templates:** `templates`, `addTemplate()`.

All API interactions (fetching, creating, deleting) are encapsulated within these store actions.

## 4. Routing (`router/index.js`)

*   Uses `createWebHistory` for clean URLs.
*   Defines routes for `/login`, `/`, `/settings`, and `/templates`.
*   Implements a `router.beforeEach` navigation guard to enforce authentication, redirecting unauthenticated users to `/login`.

## 5. API Communication

The frontend makes API calls using the native `fetch` API. All requests are made to relative paths (e.g., `/v1/organizations/`).

*   **Production (Docker):** NGINX (`nginx.conf`) acts as an API Gateway, routing requests based on subdomains:
    *   `api.watchtower.com` -> `backend` (Django API)
    *   `intake.watchtower.com` -> `intake_service` (Go ETL)
*   **Development (Native):** Vite's development server (`vite.config.js`) is configured with a proxy to route requests to `http://127.0.0.1:8000` (for Django) and `http://127.0.0.1:3000` (for Go).

## 6. Key Components

*   **`App.vue`**: The main layout component, including the `v-navigation-drawer` (sidebar), `v-app-bar` (header), and `<router-view>` for dynamic page content.
*   **`OrganizationSelector.vue`**: A dropdown in the app bar to switch between active organizations.
*   **`OrganizationManager.vue`**: A card with a form to create new organizations. After creation, it navigates to the Settings page.
*   **`ProviderSettings.vue`**: A comprehensive settings card for:
    *   Adding/viewing/deleting LLM `ProviderCredentials`.
    *   Adding/viewing/deleting `BotIntegrations`, including a `v-switch` to toggle their active status.
*   **`TemplateManager.vue`**: A `v-data-table` to display and manage instructional templates.

## 7. Development Workflow

1.  **Start Docker Infrastructure:** `docker-compose -f docker-compose.local.yml up -d`
2.  **Navigate to `frontend/` directory.**
3.  **Install dependencies:** `npm install` (or `yarn install`)
4.  **Create `.env.local`:** Copy from `.env.example` and configure `VITE_API_V1_URL` and `VITE_API_INTAKE_URL` to point to `http://127.0.0.1:8000` and `http://127.0.0.1:3000` respectively.
5.  **Start development server:** `npm run dev` (or `yarn dev`)
6.  Access the frontend at `http://localhost:8080`.
