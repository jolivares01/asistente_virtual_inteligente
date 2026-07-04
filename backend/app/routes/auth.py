from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime
from bson import ObjectId

from app.models import UsuarioLogin, TokenResponse
from app.database import get_database
from app.auth import (
    verify_password, create_access_token, get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Iniciar sesión con usuario y contraseña"""
    db = get_database()
    
    # 🔍 LOG 1: Ver qué llega desde el formulario de Swagger
    print(f"\n--- [DEBUG LOGIN] INICIO ---")
    print(f"[DEBUG LOGIN] Recibido username: '{form_data.username}'")
    print(f"[DEBUG LOGIN] Recibido password: '{form_data.password}'")
    
    # Buscar usuario por nombre de usuario
    user = await db.usuarios.find_one({"user": form_data.username})
    
    if not user:
        print(f"[DEBUG LOGIN] ❌ ERROR: El usuario '{form_data.username}' NO existe en la colección 'usuarios'.")
        print(f"--- [DEBUG LOGIN] FIN ---\n")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 🔍 LOG 2: El usuario sí existe, ver qué hash tiene guardado
    print(f"[DEBUG LOGIN]  Usuario encontrado en DB.")
    print(f"[DEBUG LOGIN] Hash en MongoDB: '{user.get('passwd')}'")
    
    # Verificar contraseña
    if not verify_password(form_data.password, user["passwd"]):
        print(f"[DEBUG LOGIN] ❌ ERROR: 'verify_password' devolvió False (Las claves no coinciden).")
        print(f"--- [DEBUG LOGIN] FIN ---\n")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"[DEBUG LOGIN]  ¡Autenticación exitosa! Procediendo a generar el token.")
    print(f"--- [DEBUG LOGIN] FIN ---\n")
    
    # Actualizar change_dt
    user_id = user["_id"]
    await db.usuarios.update_one(
        {"_id": user_id},
        {"$set": {"change_dt": datetime.utcnow()}}
    )
    
    # Crear token
    access_token = create_access_token(
        data={"sub": str(user_id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # Preparar respuesta (sin contraseña)
    user["_id"] = str(user_id)
    del user["passwd"]
    
    return TokenResponse(
        access_token=access_token,
        usuario=user
    )

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    current_user["_id"] = str(current_user["_id"])
    del current_user["passwd"]
    return current_user

@router.post("/logout")
async def logout():
    """Cerrar sesión"""
    return {"message": "Sesión cerrada exitosamente"}