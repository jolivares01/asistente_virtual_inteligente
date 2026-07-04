<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex justify-between items-center">
          <div class="flex items-center gap-4">
            <h1 class="text-2xl font-bold text-gray-900">Soporte ATC - AI</h1>
            <span class="text-sm text-gray-500">|</span>
            <span class="text-sm text-gray-600">{{ authStore.usuario?.user || 'Jesús Olivares' }}</span>
            <span class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
              Especialista de Sistemas
            </span>
          </div>
          <div class="flex items-center gap-4">
            <span class="text-sm text-gray-500">🟢 Conectado</span>
            <button @click="logout" class="text-sm text-red-600 hover:text-red-800">
              Cerrar sesión
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Columna izquierda: Tickets -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Resumen - SOLO Pendientes y Resueltos -->
          <div class="grid grid-cols-2 gap-4">
            <div class="bg-white rounded-lg shadow p-4">
              <div class="text-sm text-gray-500">Pendientes</div>
              <div class="text-2xl font-bold text-gray-900">{{ ticketsStore.pendingCount }}</div>
            </div>
            <div class="bg-white rounded-lg shadow p-4">
              <div class="text-sm text-gray-500">Resueltos</div>
              <div class="text-2xl font-bold text-green-600">{{ ticketsStore.resolvedCount }}</div>
            </div>
          </div>

          <!-- Lista de Tickets -->
          <TicketList />
        </div>

        <!-- Columna derecha: Chat -->
        <div class="lg:col-span-1">
          <ChatPanel />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useTicketsStore } from '@/stores/ticketsStore'
import TicketList from './TicketList.vue'
import ChatPanel from './ChatPanel.vue'

const authStore = useAuthStore()
const ticketsStore = useTicketsStore()
const router = useRouter()

const logout = () => {
  authStore.logout()
  router.push('/login')
}

onMounted(async () => {
  await ticketsStore.loadAllTickets()
})
</script>