from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from bson import ObjectId
from datetime import datetime
import uuid

from app.models import ChatMessage, ChatRequest, ChatResponse
from app.database import get_database
from app.auth import get_current_user
from app.ai_service import ai_service

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """Enviar un mensaje al asistente"""
    db = get_database()
    
    try:
        # Generar session_id si no existe
        session_id = request.session_id or str(uuid.uuid4())
        
        # Obtener contexto del ticket si existe
        ticket_context = None
        if request.ticket_id:
            try:
                ticket = await db.tickets.find_one({"_id": ObjectId(request.ticket_id)})
                if ticket:
                    ticket_context = f"Ticket #{ticket['id']}: {ticket['title']}\n{ticket['description']}"
            except:
                pass
        
        # Guardar mensaje del usuario
        user_msg = ChatMessage(
            session_id=session_id,
            ticket_id=request.ticket_id,
            role="user",
            content=request.message
        )
        await db.messages.insert_one(user_msg.dict(by_alias=True, exclude={"id"}))
        
        # Obtener respuesta de la IA
        ai_response = await ai_service.get_response(
            session_id, 
            request.message, 
            ticket_context
        )
        
        # Guardar respuesta del asistente
        assistant_msg = ChatMessage(
            session_id=session_id,
            ticket_id=request.ticket_id,
            role="assistant",
            content=ai_response
        )
        await db.messages.insert_one(assistant_msg.dict(by_alias=True, exclude={"id"}))
        
        return ChatResponse(response=ai_response, session_id=session_id)
        
    except Exception as e:
        print(f"Error en chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}")
async def get_history(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtener historial de una sesión"""
    db = get_database()
    
    messages = await db.messages.find(
        {"session_id": session_id}
    ).sort("timestamp", 1).to_list(length=200)
    
    return [
        {
            "role": msg["role"],
            "content": msg["content"],
            "timestamp": msg["timestamp"]
        }
        for msg in messages
    ]

@router.post("/ticket/{ticket_id}/analyze")
async def analyze_ticket_chat(
    ticket_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Analizar un ticket y generar recomendaciones en el chat"""
    db = get_database()
    
    try:
        # Obtener ticket
        ticket = await db.tickets.find_one({"_id": ObjectId(ticket_id)})
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket no encontrado")
        
        # Generar análisis
        analysis = await ai_service.analyze_incident(ticket["description"])
        
        # Crear mensaje con análisis
        session_id = str(uuid.uuid4())
        message_content = f"""🔍 **ANÁLISIS DEL TICKET #{ticket.get('id', ticket_id)}**

**📋 Categoría:** {analysis.get('category', 'General')}
**⚡ Prioridad:** {analysis.get('priority', 'Media')}

**🔍 Diagnóstico:**
{analysis.get('diagnosis', 'Análisis en progreso')}

**💡 Solución Propuesta:**
{analysis.get('solution', 'Revisar logs del sistema')}

**⚠️ Precauciones:**
{analysis.get('precautions', 'Realizar backup antes de aplicar cambios')}

¿Necesitas más detalles sobre algún punto específico?"""
        
        # Guardar mensaje
        assistant_msg = ChatMessage(
            session_id=session_id,
            ticket_id=ticket_id,
            role="assistant",
            content=message_content
        )
        await db.messages.insert_one(assistant_msg.dict(by_alias=True, exclude={"id"}))
        
        return {
            "session_id": session_id,
            "message": message_content,
            "analysis": analysis
        }
        
    except Exception as e:
        print(f"Error en análisis: {e}")
        raise HTTPException(status_code=500, detail=str(e))