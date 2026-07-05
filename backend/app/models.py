from pydantic import BaseModel, Field, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from typing import Optional, Any
from datetime import datetime
from bson import ObjectId


# =====================
# MANEJADOR DE OBJECTID PARA PYDANTIC V2
# =====================

class PyObjectId(str):
    """Clase para manejar ObjectId de MongoDB en Pydantic v2"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info=None):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, _schema: Any, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        json_schema = handler(_schema)
        json_schema.update(type="string")
        return json_schema

# =====================
# MODELO DE USUARIO
# =====================

class Usuario(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user: str
    passwd: str
    created_dt: datetime
    change_dt: datetime

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# ==========================================
# MODELOS DE BASE DE DATOS (Estructura Fiel a Mongo)
# ==========================================

class TicketPendiente(BaseModel):
    """Modelo interno para mapear tickets pendientes desde MongoDB"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    id_ticket: str
    note: Optional[str] = None
    descripcion_ticket: Optional[str] = None
    created_dt: Optional[datetime] = None
    fecha_creacion: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class TicketResuelto(BaseModel):
    """Modelo interno para mapear tickets resueltos desde MongoDB"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    id_ticket: str
    note: str  
    created_dt: datetime  

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# =====================
# DTOs para Requests/Responses (Capa de salida al Frontend)
# =====================

class UsuarioLogin(BaseModel):
    user: str
    passwd: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: dict

# ========================================================
# DTOs CONSULTA BACKEND (Campos puros mapeados por la ruta)
# ========================================================

class TicketPendienteResponse(BaseModel):
    """Estructura limpia que el Frontend (Vue 3) consume sin transformaciones complexes"""
    id_ticket: Any
    SLA_tickets: Optional[str] = "N/A"
    descripcion_ticket: str
    fecha_creacion: datetime

    class Config:
        populate_by_name = True

class TicketResueltoResponse(BaseModel):
    """Mapea correctamente desde Mongo (note/created_dt) hacia el Frontend (descripcion_ticket/fecha_creacion)"""
    id_ticket: Any
    
    note: str = Field(validation_alias="note", serialization_alias="descripcion_ticket")
    created_dt: datetime = Field(validation_alias="created_dt", serialization_alias="fecha_creacion")

    class Config:
        populate_by_name = True

# ============================================
# MODELO DEL SISTEMA EXPERTO IA
# ============================================

class TicketLifecycleAnalysis(BaseModel):
    """Esquema estricto para el análisis que devolverá Gemini"""
    title: str = Field(description="Título breve y conciso de la incidencia")
    category: str = Field(description="Categoría: red/servidor/base_datos/aplicación/seguridad/hardware/general")
    priority: str = Field(description="Prioridad analizada: baja/media/alta/crítica")
    timeline_summary: str = Field(description="Resumen de la cronología desde que se abrió hasta que se cerró")
    initial_problem: str = Field(description="Análisis del problema original basándose en el primer registro")
    resolution_actions: str = Field(description="Análisis estricto de las acciones tomadas para resolverlo en la fecha final")
    diagnosis_and_impact: str = Field(description="Causa raíz técnica e impacto evaluado en la plataforma")
    precautions: str = Field(description="Precauciones o recomendaciones preventivas para evitar que se repita")


# ============================================
# MODELOS PARA EL CHAT INTERACTIVO (IA)
# ============================================

class ChatMessage(BaseModel):
    """Modelo para persistir y mapear el histórico de interacciones en MongoDB"""
    session_id: str
    ticket_id: Optional[str] = None
    role: str  # 'user' o 'assistant'
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ChatRequest(BaseModel):
    """Modelo flexible optimizado para recibir peticiones del chat sin Warnings de Pydantic"""
    message: Optional[str] = None
    session_id: Optional[Any] = None
    ticket_id: Optional[Any] = None

    class Config:
        populate_by_name = True

    # 💡 Inicializador limpio: Unifica las propiedades dinámicamente en Python nativo
    def __init__(self, **data):
        if "mensaje" in data:
            data["message"] = data["mensaje"]
        if "content" in data:
            data["message"] = data["content"]
        if "text" in data:
            data["message"] = data["text"]
            
        if "sesion_id" in data:
            data["session_id"] = data["sesion_id"]
            
        if "id_ticket" in data:
            data["ticket_id"] = data["id_ticket"]
        if "ticket" in data and isinstance(data["ticket"], dict):
            data["ticket_id"] = data["ticket"].get("id_ticket") or data["ticket"].get("id")
            
        super().__init__(**data)

class ChatResponse(BaseModel):
    """Estructura de salida unificada para el componente de chat"""
    response: str
    session_id: str