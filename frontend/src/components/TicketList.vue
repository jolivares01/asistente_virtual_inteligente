<template>
  <div class="bg-white rounded-lg shadow">
    <div class="border-b border-gray-200">
      <div class="flex space-x-4 px-4 py-2">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key"
          class="px-4 py-2 text-sm font-medium rounded-lg transition"
          :class="[
            activeTab === tab.key
              ? 'bg-indigo-100 text-indigo-700'
              : 'text-gray-500 hover:bg-gray-100'
          ]"
        >
          {{ tab.label }}
          <span class="ml-2 text-xs bg-gray-200 px-2 py-0.5 rounded-full">
            {{ tab.count }}
          </span>
        </button>
      </div>
    </div>

    <div v-if="activeTab === 'resolved'" class="p-4 border-b border-gray-200">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Buscar en resueltos..."
        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
      />
    </div>

    <div class="divide-y divide-gray-200 max-h-[500px] overflow-y-auto">
      <div v-if="filteredTickets.length === 0" class="p-8 text-center text-gray-500">
        <p v-if="activeTab === 'pending'">No hay tickets pendientes</p>
        <p v-else>No hay tickets resueltos</p>
      </div>
      
      <TicketCard
        v-for="ticket in (filteredTickets as any[])"
        :key="`${activeTab}-${ticket.id_ticket}`"
        :ticket="ticket"
        :is-selected="chatStore.currentTicket?.id === String(ticket.id_ticket)"
        @click="selectTicket(ticket)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useTicketsStore } from '@/stores/ticketsStore'
import { useChatStore } from '@/stores/chatStore'
import TicketCard from './TicketCard.vue'

const ticketsStore = useTicketsStore()
const chatStore = useChatStore()
const activeTab = ref('pending')
const searchQuery = ref('')

const tabs = computed(() => [
  { key: 'pending', label: 'Pendientes', count: ticketsStore.pendingCount },
  { key: 'resolved', label: 'Resueltos', count: ticketsStore.resolvedCount }
])

const filteredTickets = computed(() => {
  let tickets = []
  
  if (activeTab.value === 'pending') {
    tickets = ticketsStore.ticketsPendientes || []
  } else {
    tickets = ticketsStore.ticketsResueltos || []
  }

  if (searchQuery.value && activeTab.value === 'resolved') {
    const query = searchQuery.value.toLowerCase().trim()
    tickets = tickets.filter((t: any) => {
      const idStr = String(t.id_ticket || '').toLowerCase()
      const descStr = String(t.descripcion_ticket || '').toLowerCase()
      const noteStr = String(t.note || '').toLowerCase()
      
      return descStr.includes(query) || idStr.includes(query) || noteStr.includes(query)
    })
  }

  return tickets
})

const selectTicket = (ticket: any) => {
  const idStr = String(ticket.id_ticket)
  
  // Capturamos la descripción técnica completa (note para resueltos, descripcion_ticket para pendientes)
  const fullDescription = ticket.note || ticket.descripcion_ticket || 'Sin descripción disponible.'

  // Nos aseguramos de que la fecha se procese limpiamente como string ISO
  const rawDate = ticket.fecha_creacion || ticket.created_dt
  const formattedDate = rawDate ? new Date(rawDate).toISOString() : new Date().toISOString()

  const ticketForChat = {
    id: idStr,
    title: ticket.descripcion_ticket ? ticket.descripcion_ticket.substring(0, 50) + '...' : `Ticket #${idStr}`,
    description: fullDescription,
    createdBy: ticket.creado_por || 'Sistema CRM',
    createdAt: formattedDate,
    priority: ticket.prioridad || ticket.SLA_tickets || 'Media',
    status: activeTab.value === 'pending' ? 'pending' : 'resolved'
  }
  
  chatStore.setCurrentTicket(ticketForChat)
}
</script>