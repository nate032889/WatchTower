<template>
  <v-card>
    <v-card-title>Template Manager</v-card-title>
    <v-card-text>
      <v-data-table
        :headers="headers"
        :items="templates"
        item-key="id"
        class="elevation-1"
      >
        <template v-slot:top>
          <v-toolbar flat>
            <v-toolbar-title>Templates</v-toolbar-title>
            <v-divider class="mx-4" inset vertical></v-divider>
            <v-spacer></v-spacer>
            <v-dialog v-model="dialog" max-width="500px">
              <template v-slot:activator="{ props }">
                <v-btn
                  color="primary"
                  dark
                  class="mb-2"
                  v-bind="props"
                >
                  New Template
                </v-btn>
              </template>
              <v-card>
                <v-card-title>
                  <span class="text-h5">New Template</span>
                </v-card-title>

                <v-card-text>
                  <v-container>
                    <v-row>
                      <v-col cols="12">
                        <v-text-field
                          v-model="editedItem.name"
                          label="Template Name"
                        ></v-text-field>
                      </v-col>
                      <v-col cols="12">
                        <v-textarea
                          v-model="editedItem.content"
                          label="System Prompt"
                        ></v-textarea>
                      </v-col>
                    </v-row>
                  </v-container>
                </v-card-text>

                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn color="blue-darken-1" text @click="close">
                    Cancel
                  </v-btn>
                  <v-btn color="blue-darken-1" text @click="save">
                    Save
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </v-toolbar>
        </template>
        <template v-slot:item.actions="{ item }">
          <v-icon size="small" class="me-2" @click="editItem(item)">
            mdi-pencil
          </v-icon>
          <v-icon size="small" @click="deleteItem(item)">
            mdi-delete
          </v-icon>
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAppStore } from '../stores/app'

const store = useAppStore()

const dialog = ref(false)
const headers = [
  { title: 'Name', key: 'name' },
  { title: 'Content', key: 'content' },
  { title: 'Actions', key: 'actions', sortable: false },
]

const templates = computed(() => store.templates)

const editedItem = ref({
  name: '',
  content: '',
})

const defaultItem = {
  name: '',
  content: '',
}

const close = () => {
  dialog.value = false
  editedItem.value = { ...defaultItem }
}

const save = () => {
  if (editedItem.value.name && editedItem.value.content) {
    store.addTemplate({ ...editedItem.value })
  }
  close()
}

const editItem = (item) => {
  editedItem.value = { ...item }
  dialog.value = true
}

const deleteItem = (item) => {
  const index = templates.value.findIndex(t => t.id === item.id)
  if (index > -1) {
    confirm('Are you sure you want to delete this item?') && templates.value.splice(index, 1)
  }
}
</script>
