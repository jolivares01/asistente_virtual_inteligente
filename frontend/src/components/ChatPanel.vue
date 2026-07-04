<template>
  <div class="bg-white rounded-lg shadow h-[650px] flex flex-col">
    <!-- Header -->
    <div class="p-4 border-b border-gray-200 bg-gradient-to-r from-indigo-50 to-blue-50 rounded-t-lg">
      <div class="flex justify-between items-center">
        <div>
          <h3 class="font-semibold text-gray-900">🤖 Agente de Soporte</h3>
          <p v-if="chatStore.currentTicket" class="text-sm text-gray-600">
            Analizando ticket activo #{{ chatStore.currentTicket.id }}
          </p>
          <p v-else class="text-sm text-gray-400">Selecciona un ticket para comenzar</p>
        </div>
        <div v-if="chatStore.isProcessing" class="flex items-center gap-2">
          <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span class="text-xs text-gray-500">Procesando...</span>
        </div>
      </div>
    </div>

    <!-- Messages -->
    <div class="flex-1 overflow-y-auto p-4 space-y-4" ref="messagesContainer">
      <div v-if="!chatStore.currentTicket" class="text-center text-gray-400 mt-20">
        <div class="text-4xl mb-4">💬</div>
        <p>Selecciona un ticket de la lista</p>
        <p class="text-sm">para comenzar el análisis con IA</p>
      </div>

      <div v-else-if="chatStore.messages.length === 0" class="text-center text-gray-400 mt-20">
        <div class="text-4xl mb-4">🤖</div>
        <p>¡Hola! He analizado el ticket</p>
        <p class="text-sm">¿En qué puedo ayudarte?</p>
      </div>

      <ChatMessage
        v-for="(msg, index) in chatStore.messages"
        :key="index"
        :message="msg"
      />
    </div>

    <!-- Input -->
    <div v-if="chatStore.currentTicket" class="p-4 border-t border-gray-200">
      <div class="flex gap-2">
        <input
          v-model="messageInput"
          @keyup.enter="sendMessage"
          type="text"
          placeholder="Escribe tu mensaje..."
          class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          :disabled="chatStore.isProcessing"
        />
        <button
          @click="sendMessage"
          :disabled="!messageInput.trim() || chatStore.isProcessing"
          class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          Enviar →
        </button>
      </div>
      <div class="mt-2 text-xs text-gray-400">
        <button @click="sendQuickMessage('Ver documentación interna de errores')" class="hover:text-indigo-600">
          📄 Ver documentación interna de errores
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { useChatStore } from '@/stores/chatStore'
import ChatMessage from './ChatMessage.vue'

const chatStore = useChatStore()
const messagesContainer = ref<HTMLDivElement | null>(null)
const messageInput = ref('')

const sendMessage = async () => {
  if (!messageInput.value.trim() || chatStore.isProcessing) return
  
  const message = messageInput.value
  messageInput.value = ''
  
  await chatStore.sendMessage(message)
  
  nextTick(() => {
    scrollToBottom()
  })
}

const sendQuickMessage = async (text: string) => {
  messageInput.value = text
  await sendMessage()
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

watch(() => chatStore.messages.length, () => {
  nextTick(() => scrollToBottom())
})
</script>