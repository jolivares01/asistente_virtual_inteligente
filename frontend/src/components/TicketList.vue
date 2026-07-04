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
        :key="ticket.id || ticket._id"
        :ticket="ticket"
        :is-selected="chatStore.currentTicket?.id === ticket.id_ticket"
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
    tickets = ticketsStore.ticketsPendientes
  } else {
    tickets = ticketsStore.ticketsResueltos
  }

  if (searchQuery.value && activeTab.value === 'resolved') {
    const query = searchQuery.value.toLowerCase()
    tickets = tickets.filter((t: any) => 
      t.descripcion_ticket?.toLowerCase().includes(query) ||
      t.id_ticket?.toLowerCase().includes(query) ||
      t.resolucion_ticket?.toLowerCase().includes(query)
    )
  }

  return tickets
})

const selectTicket = (ticket: any) => {
  // Convertir el ticket de la base de datos al formato que espera el chat sus interfaces
  const ticketForChat = {
    id: ticket.id_ticket,
    title: ticket.descripcion_ticket,
    description: ticket.descripcion_ticket,
    createdBy: ticket.creado_por || 'Usuario',
    createdAt: ticket.fecha_creacion || new Date().toISOString(),
    priority: ticket.prioridad || 'Media',
    status: ticket.estado || 'pending'
  }
  chatStore.setCurrentTicket(ticketForChat)
}
</script>