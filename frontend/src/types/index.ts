// Tipos para usuarios
export interface User {
  id: string
  name: string
  email: string
  role: string
}

// Tipos para tickets
export interface Ticket {
  id: string
  title: string
  description: string
  priority: 'Alta' | 'Media' | 'Baja'
  status: 'pending' | 'in_progress' | 'resolved'
  createdBy: string
  createdAt: string
  category?: string
  resolvedBy?: string
  solutionType?: string
}

// Tipos para mensajes del chat
export interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  isError?: boolean
}