from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
from app.database import get_database
from app.auth import get_current_user
from app.ai_service import ai_service

# Importamos las respuestas con alias que configuramos en models.py
from app.models import TicketPendienteResponse, TicketResueltoResponse, TicketLifecycleAnalysis

router = APIRouter(prefix="/api/tickets", tags=["tickets"])

@router.get("/pendientes", response_model=List[TicketPendienteResponse])
async def get_tickets_pendientes(
    current_user: dict = Depends(get_current_user)
):
    """Obtener todos los tickets pendientes unificando ambos formatos de BD en memoria"""
    db = get_database()
    
    # 1. Extraemos los documentos crudos sin forzar ordenamiento directo en Mongo
    # para evitar fallos si el índice temporal varía entre registros
    raw_tickets = await db.tickets_pendientes.find({}).to_list(length=100)
    
    tickets_normalizados = []
    
    # 2. Iteramos y homogeneizamos cada documento
    for ticket in raw_tickets:
        t_formateado = dict(ticket)
        
        # 💡 Normalización del Campo de Descripción:
        # Si viene como 'note', se lo asignamos a 'descripcion_ticket'
        if "note" in t_formateado and "descripcion_ticket" not in t_formateado:
            t_formateado["descripcion_ticket"] = t_formateado["note"]
        elif "descripcion_ticket" not in t_formateado:
            t_formateado["descripcion_ticket"] = "Sin descripción técnica disponible"
            
        # 💡 Normalización del Campo de Fecha:
        # Si viene como 'created_dt', se lo asignamos a 'fecha_creacion'
        if "created_dt" in t_formateado and "fecha_creacion" not in t_formateado:
            t_formateado["fecha_creacion"] = t_formateado["created_dt"]
        elif "fecha_creacion" not in t_formateado:
            t_formateado["fecha_creacion"] = datetime.utcnow()
            
        tickets_normalizados.append(t_formateado)
    
    # 3. Ordenamos de forma segura en memoria de más reciente a más antiguo
    tickets_normalizados.sort(key=lambda x: x.get("fecha_creacion"), reverse=True)
    
    # Log de diagnóstico limpio para tu consola de Uvicorn
    print(f"🔍 [Backend] Éxito unificando formatos. Pendientes listos: {len(tickets_normalizados)}")
    
    return tickets_normalizados

@router.get("/resueltos", response_model=List[TicketResueltoResponse])
async def get_tickets_resueltos(
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Obtener todos los tickets resueltos filtrados y mapeados automáticamente"""
    db = get_database()
    
    query = {}
    if search:
        search = search.strip()
        
        try:
            # 1. Si la búsqueda es numérica, buscamos el id_ticket entero o coincidencia en la nota
            search_num = int(search)
            query["$or"] = [
                {"note": {"$regex": search, "$options": "i"}},
                {"id_ticket": search_num}
            ]
        except ValueError:
            # 2. Si tiene el prefijo TK-, lo removemos para buscar el entero subyacente
            clean_search = search.upper().replace("TK-", "")
            
            try:
                search_num = int(clean_search)
                query["$or"] = [
                    {"note": {"$regex": search, "$options": "i"}},
                    {"id_ticket": search_num}
                ]
            except ValueError:
                # 3. Búsqueda de texto regular en las notas técnicas
                query = {"note": {"$regex": search, "$options": "i"}}
    
    # En resueltos sí se usa 'created_dt' porque así viene estructurado el lote desde tu archivo de carga
    tickets = await db.tickets_resueltos.find(query).sort("created_dt", -1).to_list(length=100)
    
    return tickets

@router.get("/estadisticas")
async def get_estadisticas(
    current_user: dict = Depends(get_current_user)
):
    """Obtener estadísticas de tickets"""
    db = get_database()
    
    pendientes_count = await db.tickets_pendientes.count_documents({})
    resueltos_count = await db.tickets_resueltos.count_documents({})
    
    return {
        "pendientes": pendientes_count,
        "resueltos": resueltos_count,
        "total": pendientes_count + resueltos_count
    }

# =======================================================
# NUEVO ENDPOINT: CORRELACIÓN CRONOLÓGICA Y ANÁLISIS DE IA
# =======================================================
@router.post("/analizar/{id_ticket}", response_model=dict)
async def analizar_ciclo_ticket(
    id_ticket: str,
    current_user: dict = Depends(get_current_user)
):
    """Endpoint para agrupar el historial del ticket y enviarlo al Agente Experto"""
    db = get_database()
    
    # Intentamos buscar el id tanto en formato numérico como string por si acaso
    query_id = id_ticket
    try:
        query_id = int(id_ticket)
    except ValueError:
        pass

    # 1. Buscamos TODOS los eventos de ese ticket ordenados cronológicamente (antiguo a nuevo)
    cursor = db.tickets_resueltos.find({"id_ticket": query_id}).sort("created_dt", 1)
    registros = await cursor.to_list(length=20)
    
    if not registros:
        raise HTTPException(status_code=404, detail=f"No se encontraron registros para el ticket #{id_ticket}")
        
    # 2. Construimos la línea de tiempo estructurada para que la IA entienda el ciclo de vida
    contexto_cronologico = f"=== CICLO DE VIDA DEL TICKET #{id_ticket} ===\n\n"
    
    for i, reg in enumerate(registros):
        fecha_str = reg["created_dt"].strftime("%Y-%m-%d %H:%M:%S") if isinstance(reg["created_dt"], datetime) else str(reg["created_dt"])
        
        if i == 0:
            contexto_cronologico += f"[EVENTO 1: APERTURA Y REPORTE INICIAL - Fecha: {fecha_str}]\n"
            contexto_cronologico += f"Detalles:\n{reg.get('note', '')}\n\n"
        elif i == len(registros) - 1:
            contexto_cronologico += f"[EVENTO FINAL: RESOLUCIÓN Y CIERRE - Fecha: {fecha_str}]\n"
            contexto_cronologico += f"Detalles:\n{reg.get('note', '')}\n\n"
        else:
            contexto_cronologico += f"[EVENTO INTERMEDIO: SEGUIMIENTO - Fecha: {fecha_str}]\n"
            contexto_cronologico += f"Detalles:\n{reg.get('note', '')}\n\n"
            
    # 3. Invocamos al agente_ai pasándole la cronología unificada
    analisis_ia = await ai_service.analyze_ticket_lifecycle(contexto_cronologico)
    
    # Si viene con formato Pydantic lo volcamos a diccionario para evitar warnings en la consola
    if hasattr(analisis_ia, "model_dump"):
        return analisis_ia.model_dump()
        
    return analisis_ia