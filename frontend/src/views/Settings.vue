<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1>Settings</h1>
      </v-col>
      <v-col cols="12" md="6">
        <OrganizationManager />
      </v-col>
      <v-col cols="12" md="6">
        <ProviderSettings />
      </v-col>
      <v-col cols="12">
        <Integrations />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import OrganizationManager from '../components/OrganizationManager.vue'
import ProviderSettings from '../components/ProviderSettings.vue'
import Integrations from '../components/Integrations.vue'
</script>
