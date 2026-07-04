import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

interface Usuario {
  _id: string
  user: string
  created_dt: string
  change_dt: string
}

export const useAuthStore = defineStore('auth', () => {
  const usuario = ref<Usuario | null>(null)
  const token = ref<string | null>(localStorage.getItem('token') || null)

  const login = async (username: string, password: string) => {
    try {
      // OAuth2PasswordRequestForm espera x-www-form-urlencoded
      const formData = new URLSearchParams()
      formData.append('username', username)
      formData.append('password', password)
      
      const response = await axios.post('/api/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })
      
      usuario.value = response.data.usuario
      token.value = response.data.access_token
      
      // 📝 CORRECCIÓN: Usamos el operador "as string" o guardamos directo el valor de response.data
      const accessToken = response.data.access_token as string
      localStorage.setItem('token', accessToken)
      
      axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`
      
      return response.data
    } catch (error) {
      console.error('Error de login:', error)
      throw new Error('Usuario o contraseña incorrectos')
    }
  }

  const logout = () => {
    usuario.value = null
    token.value = null
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
  }

  const isAuthenticated = () => {
    return !!token.value
  }

  return {
    usuario,
    token,
    login,
    logout,
    isAuthenticated
  }
})