import os
import httpx
import json
from dotenv import load_dotenv
from typing import Optional

# Importamos el manejador de la base de datos
from app.database import get_database

load_dotenv()

class AIService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("⚠️ GEMINI_API_KEY no configurada en el archivo .env.")
        else:
            print("✅ Gemini AI inicializado mediante conexión REST directa (API v1)")
        
        # Guardamos el historial conversacional como una lista de mensajes JSON estándar
        self.chat_sessions = {}  

    async def get_response(self, session_id: str, message: str, ticket_context: Optional[str] = None) -> str:
        """Obtener respuesta conversacional mediante llamada HTTP directa (Inmune a Bugs de parámetros)"""
        if not self.api_key:
            return "⚠️ API Key no configurada."
        
        try:
            db = get_database()
            historial_coincidencias = ""
            
            # 💡 MOTOR DE BÚSQUEDA HISTÓRICA EN TIEMPO REAL (RAG)
            if ticket_context:
                palabras_clave = []
                texto_analisis = ticket_context.upper()
                
                if "ANULACION" in texto_analisis or "ANULADA" in texto_analisis:
                    palabras_clave.extend(["ANULADA", "ANULACION", "DESASOCIO", "DESASOCIAR"])
                if "BDUC" in texto_analisis or "HOMOLOGAR" in texto_analisis:
                    palabras_clave.extend(["BDUC", "HOMOLOGA", "HOMOLOGAR"])
                if "VOLTE" in texto_analisis:
                    palabras_clave.extend(["VOLTE", "PERFIL", "EQUIPO"])
                if "REEMPLAZO" in texto_analisis or "SIM" in texto_analisis or "FECHA" in texto_analisis:
                    palabras_clave.extend(["SIM", "CRM", "ORDEN", "BULK"])
                
                if palabras_clave:
                    query_busca = {"$or": [{"note": {"$regex": kw, "$options": "i"}} for kw in set(palabras_clave)]}
                    casos_viejos = await db.tickets_resueltos.find(query_busca).limit(4).to_list(length=4)
                    
                    if casos_viejos:
                        historial_coincidencias = "\n--- PRECEDENTES HISTÓRICOS REALES ENCONTRADOS EN MONGO ---\n"
                        for cv in casos_viejos:
                            historial_coincidencias += f"• Ticket #{cv.get('id_ticket')} | Acción Aplicada: {cv.get('note').strip()}\n"
            
            system_instruction = """Eres el Líder Principal de Aseguramiento de Plataformas y Soporte Aplicativo CRM en una corporación de Telecomunicaciones.
Tu rol es diagnosticar incidentes analizando su ciclo de vida (Apertura vs. Cierre) basándote estrictamente en el histórico técnico de la compañía y los precedentes reales provistos de la base de datos.

Guía obligatoria de diagnóstico basada en Casos de Éxito Históricos:
1. Si el ticket involucra una ANULACIÓN de línea (especialmente por motivos de seguridad), tu DIAGNÓSTICO debe alinearse con el histórico corporativo que demuestra que estas incidencias se solucionan DESASOCIANDO o DESAFILIANDO el GSM en los sistemas comerciales para liberar parámetros de red.
2. Si el ticket inicial reporta un error con 'bus-subscriber-lookup' o 'GSM no asociado a ningún suscriptor', tu DIAGNÓSTICO debe orientar al equipo a verificar la comunicación del microservicio de consulta (como frontbilling-account) o reintentar la sincronización de perfiles.
3. Si el caso involucra fallas en reemplazos de SIM o eSIM que caen en estatus ERROR (especialmente en canales de atención como CDA o Agentes Autorizados), tu DIAGNÓSTICO debe señalar una desincronización o falta de homologación en la base de datos central BDUC.
4. Si la nota describe bloqueos en el CRM al ingresar datos (como la fecha de nacimiento o bloqueos en Bulk Orders), tu DIAGNÓSTICO debe indicar un desbordamiento en las colas de procesamiento del CRM o problemas de validación en los formularios del front de la plataforma.
5. Si se menciona afectación a cuentas POSPAGO o aprovisionamiento de FWA (Fixed Wireless Access), advierte siempre en las PRECAUCIONES que no se debe eliminar la cuenta o alterar el estado de la línea hasta que cierre el ciclo de facturación actual para evitar reclamos de saldo.

Mantén un tono de Ingeniero Senior de Infraestructura: conciso, predictivo, altamente técnico y guiado rigurosamente por los datos históricos adjuntos."""

            # 💡 SOLUCIÓN ESTRUCTURAL: Inyectamos el rol del sistema en el primer mensaje de inicialización
            if session_id not in self.chat_sessions:
                self.chat_sessions[session_id] = []
                
                prompt_inicial = f"INSTRUCCIONES DEL SISTEMA:\n{system_instruction}\n\nCONTEXTO OPERATIVO DEL TICKET SELECCIONADO PARA EL ANÁLISIS:\n{ticket_context}"
                if historial_coincidencias:
                    prompt_inicial += f"\n\nUsa estos precedentes históricos reales extraídos de la base de datos para responder de forma asertiva:\n{historial_coincidencias}"
                
                self.chat_sessions[session_id].append({"role": "user", "parts": [{"text": prompt_inicial}]})
                self.chat_sessions[session_id].append({"role": "model", "parts": [{"text": "Entendido. He procesado las instrucciones operativas y cruzado el ticket con el histórico de soluciones reales en MongoDB. Estoy listo para guiarte bajo la estrategia exacta de la compañía."}]})

            # Añadir la consulta actual enviada por el analista
            prompt_final = message
            if ticket_context:
                prompt_final = f"Evaluando el ticket activo:\n{ticket_context}\n"
                if historial_coincidencias:
                    prompt_final += f"Precedentes históricos en la DB:\n{historial_coincidencias}\n"
                prompt_final += f"Pregunta del Analista: {message}"

            self.chat_sessions[session_id].append({"role": "user", "parts": [{"text": prompt_final}]})

            # 💡 URL DEL ENDPOINT OFICIAL REST (API v1)
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={self.api_key}"
            
            # Enviamos el contenido puro de la conversación, evitando metadatos conflictivos a nivel de raíz
            payload = {
                "contents": self.chat_sessions[session_id],
                "generationConfig": {
                    "temperature": 0.2
                }
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=30.0)

            res_json = response.json()
            
            if "candidates" in res_json and len(res_json["candidates"]) > 0:
                texto_respuesta = res_json["candidates"][0]["content"]["parts"][0]["text"]
                # Guardamos la respuesta en memoria para mantener el hilo de la conversación
                self.chat_sessions[session_id].append({"role": "model", "parts": [{"text": texto_respuesta}]})
                return texto_respuesta
            else:
                print(f"Error en respuesta de Google REST: {res_json}")
                return "⚠️ No se pudo extraer una respuesta válida del cluster de Google."
            
        except Exception as e:
            print(f"Error en motor RAG Gemini REST Directo: {e}")
            return "⚠️ Ocurrió un error procesando el mensaje mediante la pasarela HTTP."

    async def analyze_ticket_lifecycle(self, full_ticket_context: str) -> dict:
        """Mapeo del ciclo de vida simplificado de respaldo para mantener compatibilidad de rutas"""
        return {
            "title": "Análisis del ciclo del ticket",
            "category": "aplicación",
            "priority": "alta",
            "timeline_summary": "Evaluación del flujo de eventos.",
            "initial_problem": "Solicitud entrante registrada en sistema CRM.",
            "resolution_actions": "Ejecución de desasociación en base de datos comerciales.",
            "diagnosis_and_impact": "Incidencia mitiga parámetros de red bloqueados.",
            "precautions": "No alterar el estado de la línea hasta el próximo ciclo de facturación."
        }

ai_service = AIService()