import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import axios from 'axios'
import './style.css'

// Configurar axios
axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Interceptor para agregar token
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')