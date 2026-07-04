from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    client: AsyncIOMotorClient = None
    db = None

db = Database()

async def connect_to_mongo():
    """Conectar a MongoDB"""
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB", "helpdesk_db")
    
    db.client = AsyncIOMotorClient(mongo_url)
    db.db = db.client[db_name]
    
    print(f"✅ Conectado a MongoDB en: {mongo_url}")
    print(f"📊 Base de datos: {db_name}")
    
    # Verificar que las colecciones existen
    collections = await db.db.list_collection_names()
    print(f"📁 Colecciones encontradas: {collections}")

async def close_mongo_connection():
    """Cerrar conexión a MongoDB"""
    if db.client:
        db.client.close()
        print("❌ Desconectado de MongoDB")

def get_database():
    """Obtener instancia de la base de datos"""
    return db.db