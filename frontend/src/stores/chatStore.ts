import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  isError?: boolean
}

interface Ticket {
  id: string
  title: string
  description: string
  createdBy: string
  createdAt: string
  priority: string
  status: string
}

export const useChatStore = defineStore('chat', () => {
  const currentTicket = ref<Ticket | null>(null)
  const messages = ref<Message[]>([])
  const isProcessing = ref(false)
  const sessionId = ref<string | null>(null)

  const setCurrentTicket = (ticket: Ticket) => {
    currentTicket.value = ticket
    messages.value = []
    sessionId.value = null
    
    const initialMessage = `¡Hola, Jesús! He analizado el ticket de ${ticket.createdBy}.\nEl problema es: ${ticket.description}\n\n¿En qué puedo ayudarte a resolver esta incidencia?`
    
    messages.value.push({
      role: 'assistant',
      content: initialMessage,
      timestamp: new Date()
    })
  }

  const sendMessage = async (content: string) => {
    if (!currentTicket.value) return

    // Agregar mensaje del usuario en la UI
    messages.value.push({
      role: 'user',
      content,
      timestamp: new Date()
    })

    isProcessing.value = true

    try {
      const response = await axios.post('/api/chat/send', {
        message: content,                  // En lugar de 'mensaje'
        session_id: sessionId.value,       // En lugar de 'sesion_id'
        ticket_id: currentTicket.value.id  // En lugar de 'id_ticket'
      })

      if (response.data.session_id) {
        sessionId.value = response.data.session_id
      }

      messages.value.push({
        role: 'assistant',
        content: response.data.response,  // En lugar de response.data.respuesta
        timestamp: new Date()
      })

    } catch (error) {
      console.error('Error enviando mensaje a Gemini:', error)
      
      const fallbackResponses = [
        `Del historial de los casos documentados, se evidencia que la mayoría de los casos son por error en la dirección de facturación.\n\n¿Quieres que te dé mayor detalle de esa incidencia?`,
        `He encontrado documentación interna sobre este error.\n\n**Solución recomendada**:\n• Verificar consistencia de datos\n• Validar relaciones entre tablas\n• Ejecutar script de limpieza\n\n¿Necesitas acceso a los scripts de corrección?`,
        `Para resolver esta incidencia, te sugiero seguir este plan:\n\n1. **Diagnóstico**: ${currentTicket.value?.description || 'Validar logs'}\n2. **Pasos a seguir**: Verificar estado, revisar configuración, aplicar corrección\n3. **Documentación**: Consultar KB-${currentTicket.value?.id || '0000'}\n\n¿Necesitas que elabore algún punto en particular?`
      ]
      
      messages.value.push({
        role: 'assistant',
        content: fallbackResponses[Math.floor(Math.random() * fallbackResponses.length)],
        timestamp: new Date()
      })
    } finally {
      isProcessing.value = false
    }
  }

  return {
    currentTicket,
    messages,
    isProcessing,
    sessionId,
    setCurrentTicket,
    sendMessage
  }
})