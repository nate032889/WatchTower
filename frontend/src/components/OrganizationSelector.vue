<template>
  <v-select
    v-model="activeOrganizationId"
    :items="organizations"
    item-title="name"
    item-value="id"
    label="Select Organization"
    dense
    outlined
    hide-details
    class="mx-4"
    style="max-width: 200px;"
  ></v-select>
</template>

<script setup>
import { computed } from 'vue'
import { useAppStore } from '../stores/app'

const store = useAppStore()

const activeOrganizationId = computed({
  get: () => store.activeOrganizationId,
  set: (value) => store.setActiveOrganization(value)
})

const organizations = computed(() => store.organizations)
</script>
