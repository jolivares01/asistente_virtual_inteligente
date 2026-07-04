<template>
  <div 
    @click="$emit('click')"
    class="p-4 hover:bg-gray-50 cursor-pointer transition group"
    :class="[isSelected ? 'bg-indigo-50 border-l-4 border-indigo-500' : '']"
  >
    <div class="flex justify-between items-start">
      <div class="flex-1">
        <div class="flex items-center gap-2 mb-1">
          <span 
            v-if="ticket.prioridad"
            class="px-2 py-0.5 text-xs font-medium rounded-full"
            :class="priorityClasses"
          >
            {{ ticket.prioridad }}
          </span>
          <span v-else class="px-2 py-0.5 text-xs font-medium rounded-full bg-gray-100 text-gray-600">
            Media
          </span>
          <span class="text-xs text-gray-500">
            {{ timeAgo(ticket.fecha_creacion || ticket.createdAt) }}
          </span>
        </div>
        <h4 class="font-medium text-gray-900 group-hover:text-indigo-600 transition">
          {{ ticket.descripcion_ticket || ticket.title }}
        </h4>
        <p class="text-sm text-gray-600 mt-1 line-clamp-2">
          {{ ticket.descripcion_ticket || ticket.description }}
        </p>
        <div class="flex items-center gap-4 mt-2 text-xs text-gray-500">
          <span>Por: {{ ticket.creado_por || ticket.createdBy || 'Sistema' }}</span>
          <span>ID: {{ ticket.id_ticket || ticket.id }}</span>
          <span v-if="ticket.resolucion_ticket" class="text-green-600">
            ✅ Resuelto
          </span>
        </div>
      </div>
      <div class="flex flex-col items-end gap-2">
        <div v-if="ticket.estado === 'resolved' || ticket.resolucion_ticket" 
             class="text-xs text-green-600 bg-green-50 px-2 py-1 rounded">
          Resuelto
        </div>
        <div v-else-if="ticket.estado === 'in_progress'" 
             class="text-xs text-yellow-600 bg-yellow-50 px-2 py-1 rounded">
          En progreso
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  ticket: any
  isSelected?: boolean
}>()

defineEmits(['click'])

const priorityClasses = computed(() => {
  const priority = props.ticket.prioridad || 'Media'
  return {
    'bg-red-100 text-red-800': priority === 'Alta',
    'bg-yellow-100 text-yellow-800': priority === 'Media',
    'bg-blue-100 text-blue-800': priority === 'Baja'
  }
})

const timeAgo = (date: string) => {
  if (!date) return 'Fecha desconocida'
  const diff = Date.now() - new Date(date).getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  
  if (minutes < 1) return 'Hace unos segundos'
  if (minutes < 60) return `Hace ${minutes} min`
  if (hours < 24) return `Hace ${hours} h`
  return new Date(date).toLocaleDateString()
}
</script>