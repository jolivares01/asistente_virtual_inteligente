import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/components/Login.vue'
import Dashboard from '@/components/Dashboard.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login, name: 'login' },
  { path: '/dashboard', component: Dashboard, name: 'dashboard', meta: { requiresAuth: true } }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Guardia de navegación
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router