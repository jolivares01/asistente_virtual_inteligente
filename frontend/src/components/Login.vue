<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-8">
      <!-- Logo y título -->
      <div class="text-center mb-8">
        <div class="flex justify-center mb-4">
          <div class="bg-indigo-100 p-3 rounded-full">
            <svg class="w-12 h-12 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
            </svg>
          </div>
        </div>
        <h1 class="text-2xl font-bold text-gray-900">Iniciar sesión</h1>
        <p class="text-sm text-gray-600 mt-1">Accede a tu panel de soporte optimizado con IA</p>
      </div>

      <!-- Formulario -->
      <form @submit.prevent="handleLogin" class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">USUARIO</label>
          <input
            v-model="username"
            type="text"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
            placeholder="jesus.olivares@digitel.com.ve"
            required
          />
        </div>

        <div>
          <div class="flex justify-between items-center mb-1">
            <label class="block text-sm font-medium text-gray-700">CONTRASEÑA</label>
            <button type="button" class="text-sm text-indigo-600 hover:text-indigo-800">
              ¿La olvidaste?
            </button>
          </div>
          <div class="relative">
            <input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition pr-10"
              placeholder="••••••••"
              required
            />
            <button
              type="button"
              @click="showPassword = !showPassword"
              class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
            >
              {{ showPassword ? '🙈' : '👁️' }}
            </button>
          </div>
        </div>

        <div class="flex items-center">
          <input
            v-model="rememberMe"
            type="checkbox"
            class="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
          />
          <span class="ml-2 text-sm text-gray-600">Recordar mi sesión por 30 días</span>
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-indigo-600 text-white py-3 rounded-lg font-medium hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="!loading">INICIAR →</span>
          <span v-else class="flex items-center justify-center">
            <svg class="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
            </svg>
            Procesando...
          </span>
        </button>
      </form>

      <!-- Mensaje de error -->
      <div v-if="error" class="mt-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()
const router = useRouter()

const username = ref('jesus.olivares@digitel.com.ve')
const password = ref('password123')
const rememberMe = ref(false)
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  
  try {
    await authStore.login(username.value, password.value)
    router.push('/dashboard')
  } catch (err) {
    error.value = 'Credenciales inválidas. Por favor, intenta nuevamente.'
  } finally {
    loading.value = false
  }
}
</script>