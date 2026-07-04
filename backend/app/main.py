from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.database import connect_to_mongo, close_mongo_connection
from app.routes.auth import router as auth_router
from app.routes.tickets import router as tickets_router

load_dotenv()

app = FastAPI(
    title="HelpDesk AI API",
    description="API para sistema de soporte con IA",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas
app.include_router(auth_router)
app.include_router(tickets_router)

@app.on_event("startup")
async def startup():
    await connect_to_mongo()
    print("✅ Backend iniciado correctamente")

@app.on_event("shutdown")
async def shutdown():
    await close_mongo_connection()

@app.get("/")
async def root():
    return {
        "message": "HelpDesk AI API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}