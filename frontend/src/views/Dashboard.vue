<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1>Dashboard</h1>
        <p v-if="store.activeOrganizationId">
          Showing status for Organization ID: {{ store.activeOrganizationId }}
        </p>
        <p v-else>Please select an organization.</p>
      </v-col>

      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Bot Integration Status</v-card-title>
          <v-list>
            <v-list-item
              v-for="platform in ['discord', 'slack', 'mattermost']"
              :key="platform"
            >
              <v-list-item-title>{{ platform.charAt(0).toUpperCase() + platform.slice(1) }}</v-list-item-title>
              <template v-slot:append>
                <v-chip :color="getIntegrationStatus(platform) ? 'green' : 'red'">
                  {{ getIntegrationStatus(platform) ? 'Active' : 'Inactive' }}
                </v-chip>
              </template>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { useAppStore } from '../stores/app'

const store = useAppStore()

const getIntegrationStatus = (platform) => {
  // Guard Clause: If integrations haven't been loaded yet, return false.
  if (!Array.isArray(store.integrations)) {
    return false;
  }

  const integration = store.integrations.find(
    (integ) => integ.platform === platform && integ.is_active
  );
  return !!integration;
};
</script>
