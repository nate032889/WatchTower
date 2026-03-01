import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    activeOrganizationId: null,
    selectedTemplateId: null,
    organizations: [
      { id: 1, name: 'Acme Corp' },
      { id: 2, name: 'Globex' }
    ],
    templates: [
      { id: 1, name: 'Standard Response', content: 'You are a helpful assistant.' },
      { id: 2, name: 'Technical Support', content: 'You are a technical support agent.' }
    ]
  }),
  actions: {
    setActiveOrganization(id) {
      this.activeOrganizationId = id
    },
    setSelectedTemplate(id) {
      this.selectedTemplateId = id
    },
    addTemplate(template) {
      this.templates.push({
        id: this.templates.length + 1,
        ...template
      })
    }
  }
})
