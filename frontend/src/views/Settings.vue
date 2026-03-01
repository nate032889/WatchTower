<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1>Settings</h1>
        <p class="mb-4">Manage your organizations and their credentials.</p>
      </v-col>

      <!-- Each component now gets its own full-width column to stack them -->
      <v-col cols="12">
        <OrganizationManager />
      </v-col>

      <v-col cols="12">
        <ProviderSettings />
      </v-col>

    </v-row>
  </v-container>
</template>

<script setup>
import OrganizationManager from '../components/OrganizationManager.vue'
import ProviderSettings from '../components/ProviderSettings.vue'
</script>
