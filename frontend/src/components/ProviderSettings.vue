<template>
  <!-- Provider Credentials Management -->
  <v-card>
    <v-card-title>Provider Credentials</v-card-title>
    <v-card-text>
      <v-list-subheader>Existing Credentials</v-list-subheader>
      <v-list dense>
        <v-list-item v-for="cred in store.providerCredentials" :key="cred.id">
          <v-list-item-title>{{ cred.provider.toUpperCase() }}</v-list-item-title>
          <template v-slot:append>
            <v-btn icon="mdi-delete" variant="text" @click="store.deleteProviderCredential(cred.id)"></v-btn>
          </template>
        </v-list-item>
        <v-list-item v-if="store.providerCredentials.length === 0">
          <v-list-item-title class="text-grey">No credentials saved for this organization.</v-list-item-title>
        </v-list-item>
      </v-list>

      <v-divider class="my-4"></v-divider>
      <v-list-subheader>Add New Credential</v-list-subheader>
      <v-form ref="form" v-model="valid">
        <v-select v-model="provider" :items="providers" label="LLM Provider" required></v-select>
        <v-text-field v-model="apiKey" label="API Key" type="password" required></v-text-field>
        <v-btn color="primary" @click="saveSettings" :disabled="!valid">Save Credentials</v-btn>
      </v-form>
    </v-card-text>
  </v-card>

  <!-- Bot Integrations Management -->
  <v-card class="mt-4">
    <v-card-title>Bot Integrations</v-card-title>
    <v-card-text>
      <v-list-subheader>Existing Integrations</v-list-subheader>
      <v-list dense>
        <v-list-item v-for="integ in store.botIntegrations" :key="integ.id">
          <v-list-item-title>{{ integ.platform.charAt(0).toUpperCase() + integ.platform.slice(1) }}</v-list-item-title>
          <template v-slot:append>
            <v-switch
              :model-value="integ.is_active"
              @change="store.toggleBotStatus(integ)"
              color="success"
              hide-details
              class="mr-2"
            ></v-switch>
            <v-btn icon="mdi-delete" variant="text" @click="store.deleteBotIntegration(integ.id)"></v-btn>
          </template>
        </v-list-item>
        <v-list-item v-if="store.botIntegrations.length === 0">
          <v-list-item-title class="text-grey">No integrations saved for this organization.</v-list-item-title>
        </v-list-item>
      </v-list>

      <v-divider class="my-4"></v-divider>
      <v-list-subheader>Add New Integration</v-list-subheader>
      <v-form ref="integrationForm" v-model="integrationValid">
        <v-select v-model="integrationPlatform" :items="integrationPlatforms" label="Platform" required></v-select>
        <v-text-field v-model="botToken" label="Bot Token / OAuth Key" type="password" required></v-text-field>
        <v-btn color="primary" @click="saveIntegration" :disabled="!integrationValid">Save Integration</v-btn>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup>
// ... (script content remains largely the same)
import { ref, computed } from 'vue'
import { useAppStore } from '../stores/app'

const store = useAppStore()

// --- Provider Settings ---
const valid = ref(false)
const provider = ref('Gemini')
const apiKey = ref('')
const providers = ['Gemini', 'OpenAI', 'Anthropic']
const activeOrganizationId = computed(() => store.activeOrganizationId)

const saveSettings = async () => {
  if (!activeOrganizationId.value) {
    alert('Please select an organization first.')
    return
  }
  try {
    const response = await fetch('/v1/provider-credentials/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        organization: activeOrganizationId.value,
        provider: provider.value.toLowerCase(),
        api_key: apiKey.value,
      })
    });
    if (!response.ok) throw new Error('Failed to save credentials');
    apiKey.value = '';
    await store.fetchProviderCredentials();
  } catch (error) {
    console.error('Error saving provider credentials:', error);
    alert(error.message);
  }
}

// --- Integration Settings ---
const integrationValid = ref(false)
const integrationPlatform = ref('Discord')
const botToken = ref('')
const integrationPlatforms = ['Discord', 'Slack', 'Mattermost']

const saveIntegration = async () => {
  if (!activeOrganizationId.value) {
    alert('Please select an organization first.')
    return
  }
  try {
    const response = await fetch('/v1/bot-integrations/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        organization: activeOrganizationId.value,
        platform: integrationPlatform.value.toLowerCase(),
        bot_token: botToken.value,
        is_active: true
      })
    });
    if (!response.ok) throw new Error('Failed to save integration');
    botToken.value = '';
    await store.fetchBotIntegrations();
  } catch (error) {
    console.error('Error saving integration:', error);
    alert(error.message);
  }
}
</script>
