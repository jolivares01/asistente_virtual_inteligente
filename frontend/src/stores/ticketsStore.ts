import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import type { Ticket } from '@/types'

export const useTicketsStore = defineStore('tickets', () => {
  const ticketsPendientes = ref<Ticket[]>([])
  const ticketsResueltos = ref<Ticket[]>([])
  const loading = ref(false)

  // Cargar tickets pendientes desde el backend
  const loadTicketsPendientes = async () => {
    loading.value = true
    try {
      const response = await axios.get('/api/tickets/pendientes')
      ticketsPendientes.value = response.data
      // 💡 LOG DE DIAGNÓSTICO CRUCIAL
      console.log('[Store] Tickets Pendientes cargados con éxito:', response.data)
    } catch (error) {
      console.error('[Store] Error cargando tickets pendientes:', error)
    } finally {
      loading.value = false
    }
  }

  // Cargar tickets resueltos desde el backend
  const loadTicketsResueltos = async () => {
    loading.value = true
    try {
      const response = await axios.get('/api/tickets/resueltos')
      ticketsResueltos.value = response.data
      console.log('[Store] Tickets Resueltos cargados con éxito:', response.data)
    } catch (error) {
      console.error('[Store] Error cargando tickets resueltos:', error)
    } finally {
      loading.value = false
    }
  }

  // Cargar todos los tickets de forma simultánea
  const loadAllTickets = async () => {
    await Promise.all([
      loadTicketsPendientes(),
      loadTicketsResueltos()
    ])
  }

  // Propiedades computadas para los contadores de las pestañas
  const pendingCount = computed(() => ticketsPendientes.value.length)
  const resolvedCount = computed(() => ticketsResueltos.value.length)

  return {
    ticketsPendientes,
    ticketsResueltos,
    loading,
    loadTicketsPendientes,
    loadTicketsResueltos,
    loadAllTickets,
    pendingCount,
    resolvedCount
  }
})