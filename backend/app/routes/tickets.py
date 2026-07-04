from fastapi import APIRouter, Depends
from typing import Optional
from app.database import get_database
from app.auth import get_current_user

router = APIRouter(prefix="/api/tickets", tags=["tickets"])

@router.get("/pendientes")
async def get_tickets_pendientes(
    current_user: dict = Depends(get_current_user)
):
    """Obtener todos los tickets pendientes"""
    db = get_database()
    
    tickets = await db.tickets_pendientes.find().sort("fecha_creacion", -1).to_list(length=100)
    
    # Convertir ObjectId a string
    for ticket in tickets:
        ticket["_id"] = str(ticket["_id"])
    
    return tickets

@router.get("/resueltos")
async def get_tickets_resueltos(
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Obtener todos los tickets resueltos"""
    db = get_database()
    
    query = {}
    if search:
        query["$or"] = [
            {"descripcion_ticket": {"$regex": search, "$options": "i"}},
            {"id_ticket": {"$regex": search, "$options": "i"}},
            {"resolucion_ticket": {"$regex": search, "$options": "i"}}
        ]
    
    tickets = await db.tickets_resueltos.find(query).sort("fecha_resolucion", -1).to_list(length=100)
    
    for ticket in tickets:
        ticket["_id"] = str(ticket["_id"])
    
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