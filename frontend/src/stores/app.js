import { defineStore } from 'pinia'
import router from '../router'

export const useAppStore = defineStore('app', {
  state: () => ({
    isAuthenticated: false,
    user: null,
    activeOrganizationId: null,
    organizations: [],
    providerCredentials: [],
    botIntegrations: [],
    templates: [
      { id: 1, name: 'Standard Response', content: 'You are a helpful assistant.' },
      { id: 2, name: 'Technical Support', content: 'You are a technical support agent.' }
    ],
  }),
  actions: {
    // --- AUTH ---
    async login(username, password) {
      // Mock authentication
      if (username === 'admin' && password === 'admin') {
        this.isAuthenticated = true;
        this.user = { name: 'Admin User', email: 'admin@watchtower.com' };
        
        // Fetch initial data required for the app to function
        await this.fetchOrganizations();
        
        router.push('/');
      } else {
        alert('Invalid credentials');
      }
    },
    logout() {
      this.isAuthenticated = false;
      this.user = null;
      this.activeOrganizationId = null;
      this.organizations = [];
      this.providerCredentials = [];
      this.botIntegrations = [];
      router.push('/login');
    },

    // --- ORGANIZATIONS ---
    setActiveOrganization(id) {
      this.activeOrganizationId = id;
      this.fetchProviderCredentials();
      this.fetchBotIntegrations();
    },
    async fetchOrganizations() {
      try {
        const response = await fetch('/v1/organizations/');
        if (!response.ok) throw new Error('Failed to fetch organizations');
        this.organizations = await response.json();
        if (this.organizations.length > 0 && !this.organizations.some(o => o.id === this.activeOrganizationId)) {
          this.setActiveOrganization(this.organizations[0].id);
        } else if (this.organizations.length === 0) {
          this.activeOrganizationId = null;
        }
      } catch (error) {
        console.error('Error fetching organizations:', error);
      }
    },
    async createOrganization(name) {
      try {
        const response = await fetch('/v1/organizations/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name })
        });
        if (!response.ok) throw new Error('Failed to create organization');
        await this.fetchOrganizations(); // Re-fetch the list to get the new org
        router.push('/settings'); // Navigate to settings after creation
      } catch (error) {
        console.error('Error creating organization:', error);
      }
    },

    // --- PROVIDER CREDENTIALS ---
    async fetchProviderCredentials() {
      if (!this.activeOrganizationId) return;
      try {
        const response = await fetch(`/v1/provider-credentials/?organization=${this.activeOrganizationId}`);
        if (!response.ok) throw new Error('Failed to fetch credentials');
        this.providerCredentials = await response.json();
      } catch (error) {
        console.error('Error fetching provider credentials:', error);
        this.providerCredentials = [];
      }
    },
    async deleteProviderCredential(id) {
        try {
            await fetch(`/v1/provider-credentials/${id}/`, { method: 'DELETE' });
            await this.fetchProviderCredentials();
        } catch (error) {
            console.error('Error deleting provider credential:', error);
        }
    },

    // --- BOT INTEGRATIONS ---
    async fetchBotIntegrations() {
      if (!this.activeOrganizationId) {
          this.botIntegrations = [];
          return;
      }
      try {
        const response = await fetch(`/v1/bot-integrations/?organization=${this.activeOrganizationId}`);
        if (!response.ok) throw new Error('Failed to fetch bot integrations');
        this.botIntegrations = await response.json();
      } catch (error) {
        console.error('Error fetching bot integrations:', error);
        this.botIntegrations = [];
      }
    },
    async deleteBotIntegration(id) {
        try {
            await fetch(`/v1/bot-integrations/${id}/`, { method: 'DELETE' });
            await this.fetchBotIntegrations();
        } catch (error) {
            console.error('Error deleting bot integration:', error);
        }
    },
    async toggleBotStatus(integration) {
        try {
            const response = await fetch(`/v1/bot-integrations/${integration.id}/`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ is_active: !integration.is_active })
            });
            if (!response.ok) throw new Error('Failed to update bot status');
            // Optimistically update UI, but also refetch for consistency
            await this.fetchBotIntegrations();
        } catch (error) {
            console.error('Error toggling bot status:', error);
        }
    },
    
    // --- TEMPLATES ---
    addTemplate(template) {
      this.templates.push({
        id: this.templates.length + 1,
        ...template
      })
    }
  }
})
