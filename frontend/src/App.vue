<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from './stores/authStore'
import axios from 'axios'

const authStore = useAuthStore()

onMounted(() => {
  // Restaurar sesión si existe
  const token = localStorage.getItem('token')
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
  }
})
</script>