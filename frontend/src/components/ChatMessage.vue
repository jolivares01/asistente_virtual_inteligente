<template>
  <div class="flex items-start gap-3" :class="[isAI ? '' : 'flex-row-reverse']">
    <div class="flex-shrink-0">
      <div 
        class="w-8 h-8 rounded-full flex items-center justify-center text-sm"
        :class="[isAI ? 'bg-green-100 text-green-600' : 'bg-indigo-100 text-indigo-600']"
      >
        {{ isAI ? '🤖' : '👤' }}
      </div>
    </div>
    <div 
      class="max-w-[85%] rounded-lg p-3"
      :class="[
        isAI 
          ? 'bg-gray-100 text-gray-800' 
          : 'bg-indigo-600 text-white'
      ]"
    >
      <div class="text-sm whitespace-pre-line" v-html="formattedContent"></div>
      <div 
        class="text-xs mt-1"
        :class="[isAI ? 'text-gray-500' : 'text-indigo-200']"
      >
        {{ formatTime(message.timestamp) }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Message } from '@/types'

const props = defineProps<{
  message: Message
}>()

const isAI = computed(() => props.message.role === 'assistant')

const formattedContent = computed(() => {
  let content = props.message.content
  content = content.replace(/\n/g, '<br>')
  content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  content = content.replace(/`(.*?)`/g, '<code class="bg-gray-200 dark:bg-gray-700 px-1 py-0.5 rounded">$1</code>')
  return content
})

const formatTime = (date: Date) => {
  return new Date(date).toLocaleTimeString('es-ES', {
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>