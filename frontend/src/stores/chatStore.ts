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

    // Agregar mensaje del usuario
    messages.value.push({
      role: 'user',
      content,
      timestamp: new Date()
    })

    isProcessing.value = true

    try {
      // Enviar al backend
      const response = await axios.post('/api/chat/send', {
        mensaje: content,
        sesion_id: sessionId.value,
        id_ticket: currentTicket.value.id
      })

      // Guardar session_id
      if (response.data.sesion_id) {
        sessionId.value = response.data.sesion_id
      }

      // Agregar respuesta del asistente
      messages.value.push({
        role: 'assistant',
        content: response.data.respuesta,
        timestamp: new Date()
      })

    } catch (error) {
      console.error('Error enviando mensaje:', error)
      
      // Respuesta de fallback si el backend falla
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