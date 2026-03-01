<template>
  <v-card>
    <v-card-title>Create Organization</v-card-title>
    <v-card-text>
      <v-form ref="form" v-model="valid" @submit.prevent="create">
        <v-text-field
          v-model="name"
          label="New Organization Name"
          required
          :rules="[v => !!v || 'Name is required']"
        ></v-text-field>
        <v-btn type="submit" color="primary" :disabled="!valid">Create</v-btn>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref } from 'vue'
import { useAppStore } from '../stores/app'

const store = useAppStore()
const valid = ref(false)
const name = ref('')

const create = async () => {
  if (valid.value) {
    await store.createOrganization(name.value)
    name.value = '' // Reset form
  }
}
</script>
