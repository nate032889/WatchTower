<template>
  <v-app>
    <template v-if="store.isAuthenticated">
      <v-navigation-drawer app permanent>
        <v-list>
          <v-list-item
            :prepend-avatar="`https://randomuser.me/api/portraits/men/85.jpg`"
            :title="store.user?.name"
            :subtitle="store.user?.email"
          ></v-list-item>
        </v-list>

        <v-divider></v-divider>

        <v-list density="compact" nav>
          <v-list-item prepend-icon="mdi-view-dashboard" title="Dashboard" value="dashboard" to="/"></v-list-item>
          <v-list-item prepend-icon="mdi-cog" title="Settings" value="settings" to="/settings"></v-list-item>
          <v-list-item prepend-icon="mdi-text-box" title="Templates" value="templates" to="/templates"></v-list-item>
        </v-list>

        <template v-slot:append>
          <div class="pa-2">
            <v-btn block @click="store.logout()">
              Logout
            </v-btn>
          </div>
        </template>
      </v-navigation-drawer>

      <v-app-bar app color="primary" dark>
        <v-toolbar-title>WatchTower</v-toolbar-title>
        <v-spacer></v-spacer>
        <OrganizationSelector />
      </v-app-bar>

      <v-main>
        <router-view />
      </v-main>
    </template>
    <template v-else>
      <router-view />
    </template>
  </v-app>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAppStore } from './stores/app'
import OrganizationSelector from './components/OrganizationSelector.vue'

const store = useAppStore()

onMounted(() => {
  if (store.isAuthenticated) {
    store.fetchOrganizations()
  }
})
</script>
