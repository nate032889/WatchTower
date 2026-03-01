<template>
  <v-card>
    <v-card-title>Bot Integrations</v-card-title>
    <v-card-text>
      <v-form ref="form" v-model="valid">
        <v-select
          v-model="platform"
          :items="platforms"
          label="Platform"
          required
        ></v-select>

        <v-text-field
          v-model="botToken"
          label="Bot Token / OAuth Key"
          type="password"
          required
        ></v-text-field>

        <v-btn
          color="primary"
          @click="saveIntegration"
          :disabled="!valid"
        >
          Save Integration
        </v-btn>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAppStore } from '../stores/app'

const store = useAppStore()
const valid = ref(false)
const platform = ref('Discord')
const botToken = ref('')

const platforms = ['Discord', 'Slack', 'Mattermost']

const activeOrganizationId = computed(() => store.activeOrganizationId)

const saveIntegration = async () => {
  if (!activeOrganizationId.value) {
    alert('Please select an organization first.')
    return
  }

  try {
    const response = await fetch('/api/v1/integrations/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        organization: activeOrganizationId.value,
        platform: platform.value.toLowerCase(),
        bot_token: botToken.value,
        is_active: true
      })
    })
    if (!response.ok) {
      throw new Error('Failed to save integration.')
    }
    alert('Integration saved successfully!')
    // Optionally, clear the form
    botToken.value = ''
  } catch (error) {
    console.error('Error saving integration:', error)
    alert(error.message)
  }
}
</script>
