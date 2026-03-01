<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <v-toolbar-title>WatchTower</v-toolbar-title>
      <v-spacer></v-spacer>
      <OrganizationSelector />
    </v-app-bar>

    <v-main>
      <v-container>
        <v-row>
          <v-col cols="12" md="6">
            <ProviderSettings />
          </v-col>
          <v-col cols="12" md="6">
            <TemplateManager />
          </v-col>
          <v-col cols="12">
            <Integrations />
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import OrganizationSelector from './components/OrganizationSelector.vue'
import ProviderSettings from './components/ProviderSettings.vue'
import TemplateManager from './components/TemplateManager.vue'
import Integrations from './components/Integrations.vue'
</script>
