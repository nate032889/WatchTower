<template>
  <v-card>
    <v-card-title>Provider Settings</v-card-title>
    <v-card-text>
      <v-form ref="form" v-model="valid">
        <v-select
          v-model="provider"
          :items="providers"
          label="LLM Provider"
          required
        ></v-select>

        <v-text-field
          v-model="apiKey"
          label="API Key"
          type="password"
          required
        ></v-text-field>

        <v-btn
          color="primary"
          @click="saveSettings"
          :disabled="!valid"
        >
          Save
        </v-btn>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref } from 'vue'

const valid = ref(false)
const provider = ref('Gemini')
const apiKey = ref('')

const providers = ['Gemini', 'ChatGPT', 'Claude']

const saveSettings = () => {
  // In a real app, this would call an API endpoint
  console.log('Saving settings:', { provider: provider.value, apiKey: apiKey.value })
  // Example API call:
  // fetch('/api/v1/settings', {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify({ provider: provider.value, apiKey: apiKey.value })
  // })
}
</script>
