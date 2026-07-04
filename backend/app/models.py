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
        """Método para generar el schema JSON (NUEVO para Pydantic v2)"""
        json_schema = handler(_schema)
        json_schema.update(type="string")
        return json_schema

# =====================
# MODELOS DE USUARIO
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

# =====================
# MODELOS DE TICKETS
# =====================

class TicketPendiente(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    id_ticket: str
    descripcion_ticket: str
    SLA_tickets: str
    fecha_creacion: datetime

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class TicketResuelto(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    id_ticket: str
    descripcion_ticket: str
    resolucion_ticket: str
    fecha_resolucion: datetime

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# =====================
# DTOs para Requests/Responses
# =====================

class UsuarioLogin(BaseModel):
    user: str
    passwd: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: dict

class TicketPendienteResponse(BaseModel):
    id_ticket: str
    descripcion_ticket: str
    SLA_tickets: str
    fecha_creacion: datetime

class TicketResueltoResponse(BaseModel):
    id_ticket: str
    descripcion_ticket: str
    resolucion_ticket: str
    fecha_resolucion: datetime