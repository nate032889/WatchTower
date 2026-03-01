import { createRouter, createWebHistory } from 'vue-router'
import { useAppStore } from '../stores/app'

import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import Settings from '../views/Settings.vue'
import Templates from '../views/Templates.vue'

const routes = [
  { path: '/login', name: 'Login', component: Login },
  { path: '/', name: 'Dashboard', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/settings', name: 'Settings', component: Settings, meta: { requiresAuth: true } },
  { path: '/templates', name: 'Templates', component: Templates, meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const store = useAppStore()
  if (to.meta.requiresAuth && !store.isAuthenticated) {
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router
