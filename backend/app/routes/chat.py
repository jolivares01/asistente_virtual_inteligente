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
    """Enviar un mensaje al asistente forzando la extracción real del contexto híbrido"""
    db = get_database()
    
    # 💡 BLOQUE DE AUDITORÍA INTEGRADO:
    # Esto imprimirá en tu terminal de Uvicorn las propiedades exactas del payload entrante.
    print("\n=================== AUDITORÍA CHAT ===================")
    print(f"📥 ID de Sesión recibido: '{request.session_id}'")
    print(f"📥 ID de Ticket recibido: '{request.ticket_id}'")
    print(f"📥 Mensaje del Analista: '{request.message}'")
    print("======================================================\n")

    if not request.message or str(request.message).strip() == "":
        return ChatResponse(
            response="⚠️ No se recibió texto por parte del analista para procesar en el chat.",
            session_id=request.session_id or str(uuid.uuid4())    
        )
    try:
        session_id = request.session_id or str(uuid.uuid4())
        ticket_context = None
        
        if request.ticket_id:
            # 💡 BLINDAJE EXTRA: Buscamos por _id (si es un ObjectId válido) o por id_ticket directo
            query_alternativa = {"id_ticket": request.ticket_id}
            
            # Si el ticket_id tiene forma de número de negocio, intentamos pasarlo a entero por si acaso
            try:
                query_alternativa = {"id_ticket": int(request.ticket_id)}
            except ValueError:
                if "-" in str(request.ticket_id):
                    query_alternativa = {"id_ticket": str(request.ticket_id)}

            # Intentamos armar la consulta por ObjectId si cumple con el formato hexadecimal de 24 caracteres
            query_id = None
            if len(str(request.ticket_id)) == 24:
                try:
                    query_id = {"_id": ObjectId(request.ticket_id)}
                except:
                    pass

            # Ejecutamos las búsquedas secuenciales en las colecciones reales de tu DB
            ticket = None
            if query_id:
                ticket = await db.tickets_pendientes.find_one(query_id) or await db.tickets_resueltos.find_one(query_id)
            
            if not ticket:
                ticket = await db.tickets_pendientes.find_one(query_alternativa) or await db.tickets_resueltos.find_one(query_alternativa)
            
            # Si encontramos el documento, extraemos el texto para alimentar la IA
            if ticket:
                id_negocio = ticket.get("id_ticket", "N/A")
                descripcion = ticket.get("note") or ticket.get("descripcion_ticket") or "Sin descripción"
                ticket_context = f"Ticket #{id_negocio}\nDetalle Técnico de la Incidencia:\n{descripcion}"
            else:
                # Respaldo rápido: Si no se encuentra en DB, usamos el mensaje actual como contexto temporal
                print(f"⚠️ [Chat] No se localizó el ticket {request.ticket_id} en la DB. Usando flujo preventivo.")

        # Guardar mensaje del usuario en el histórico de Mongo
        user_msg = ChatMessage(
            session_id=session_id,
            ticket_id=request.ticket_id,
            role="user",
            content=request.message
        )
        await db.messages.insert_one(user_msg.dict(by_alias=True, exclude={"id"}))
        
        # 🚀 LLAMADA A LA IA REAL OPTIMIZADA:
        ai_response = await ai_service.get_response(
            session_id=session_id, 
            message=request.message, 
            ticket_context=ticket_context
        )
        
        # Guardar respuesta de Gemini en el histórico de Mongo
        assistant_msg = ChatMessage(
            session_id=session_id,
            ticket_id=request.ticket_id,
            role="assistant",
            content=ai_response
        )
        await db.messages.insert_one(assistant_msg.dict(by_alias=True, exclude={"id"}))
        
        return ChatResponse(response=ai_response, session_id=session_id)
        
    except Exception as e:
        print(f"❌ Error crítico en flujo de chat: {e}")
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
    """Analizar el ciclo de vida del ticket usando el esquema estructurado de Gemini"""
    db = get_database()
    
    try:
        # 💡 CORRECCIÓN: Buscamos el ticket en las colecciones reales de tu DB
        ticket = await db.tickets_pendientes.find_one({"_id": ObjectId(ticket_id)})
        if not ticket:
            ticket = await db.tickets_resueltos.find_one({"_id": ObjectId(ticket_id)})
            
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket no encontrado en ninguna colección")
        
        id_negocio = ticket.get("id_ticket", "N/A")
        descripcion = ticket.get("note") or ticket.get("descripcion_ticket") or "Sin descripción"
        full_context = f"Ticket #{id_negocio}\nHistorial:\n{descripcion}"
        
        # 💡 CORRECCIÓN DE MÉTODO: Llamamos a analyze_ticket_lifecycle que implementamos en models y ai_service
        analysis = await ai_service.analyze_ticket_lifecycle(full_context)
        
        # Construimos el mensaje de respuesta apoyándonos en el contrato exacto de Pydantic
        message_content = f"""🔍 **ANÁLISIS DEL TICKET #{id_negocio}**

**📋 Categoría:** {analysis.get('category', 'General').upper()}
**⚡ Prioridad:** {analysis.get('priority', 'Media').upper()}

**📌 Resumen Cronológico:**
{analysis.get('timeline_summary', 'No disponible')}

**🔍 Problema Inicial:**
{analysis.get('initial_problem', 'No disponible')}

**🛠️ Acciones de Resolución Sugeridas:**
{analysis.get('resolution_actions', 'No disponible')}

**💡 Diagnóstico e Impacto:**
{analysis.get('diagnosis_and_impact', 'No disponible')}

**⚠️ Precauciones Corporativas:**
{analysis.get('precautions', 'No disponible')}

¿Deseas profundizar en las políticas de BDUC o CRM para mitigar este incidente?"""
        
        session_id = str(uuid.uuid4())
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
        print(f"❌ Error en endpoint analyze: {e}")
        raise HTTPException(status_code=500, detail=str(e))