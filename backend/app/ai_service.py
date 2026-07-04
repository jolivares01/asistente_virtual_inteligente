import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Optional
import json

load_dotenv()

class AIService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️ GEMINI_API_KEY no configurada. Usando respuestas simuladas.")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction="""Eres un asistente experto en IT especializado en analizar incidencias de soporte técnico.

Tu flujo de trabajo:
1. Analiza la descripción del problema o log de errores
2. Pregunta por detalles específicos si falta información
3. Propone diagnósticos y soluciones estructuradas
4. Basa tus respuestas en mejores prácticas de IT

Formato de respuesta:
- 🔍 DIAGNÓSTICO: (análisis del problema)
- 💡 SOLUCIÓN: (pasos a seguir)
- ⚠️ PRECAUCIONES: (si aplica)

Sé conciso, profesional y estructurado."""
            )
            print("✅ Gemini AI inicializado")
        
        self.chat_histories = {}  # Guarda historial por sesión

    async def get_response(self, session_id: str, message: str, ticket_context: Optional[str] = None) -> str:
        """Obtener respuesta del asistente"""
        if not self.model:
            # Respuestas simuladas si no hay API key
            return self._get_simulated_response(message, ticket_context)
        
        try:
            if session_id not in self.chat_histories:
                # Iniciar nuevo chat con contexto si existe
                history = []
                if ticket_context:
                    history.append({
                        "role": "user",
                        "parts": [f"Contexto del ticket: {ticket_context}"]
                    })
                    history.append({
                        "role": "model",
                        "parts": ["Entendido, analizaré la incidencia con este contexto."]
                    })
                
                self.chat_histories[session_id] = self.model.start_chat(history=history)
            
            chat = self.chat_histories[session_id]
            response = chat.send_message(message, stream=False)
            
            return response.text
            
        except Exception as e:
            print(f"Error en Gemini: {e}")
            return self._get_simulated_response(message, ticket_context)

    async def analyze_incident(self, description: str) -> dict:
        """Analizar una incidencia y generar solución"""
        if not self.model:
            return self._get_simulated_analysis(description)
        
        try:
            prompt = f"""
            Analiza esta incidencia como experto en sistemas:
            
            {description}
            
            Proporciona un análisis estructurado en formato JSON:
            {{
                "title": "Título breve para la incidencia",
                "category": "categoría (red/servidor/base_datos/aplicación/seguridad/hardware)",
                "priority": "prioridad (baja/media/alta/crítica)",
                "diagnosis": "posible causa raíz",
                "solution": "pasos de diagnóstico y solución propuesta",
                "precautions": "precauciones a tomar"
            }}
            """
            
            response = self.model.generate_content(prompt)
            # Intentar parsear JSON
            try:
                # Extraer JSON del texto
                text = response.text
                start = text.find('{')
                end = text.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = text[start:end]
                    return json.loads(json_str)
            except:
                pass
            
            # Si no se puede parsear, devolver texto plano
            return {
                "title": "Análisis de incidencia",
                "category": "general",
                "priority": "media",
                "diagnosis": response.text,
                "solution": "Revisar logs del sistema y validar configuración",
                "precautions": "Hacer backup antes de aplicar cambios"
            }
            
        except Exception as e:
            print(f"Error en análisis: {e}")
            return self._get_simulated_analysis(description)

    def _get_simulated_response(self, message: str, ticket_context: Optional[str] = None) -> str:
        """Respuestas simuladas para demo"""
        responses = [
            f"🔍 **DIAGNÓSTICO**: Basado en la información proporcionada, el problema parece estar relacionado con la configuración del sistema.",
            f"💡 **SOLUCIÓN**: Te sugiero seguir estos pasos:\n1. Verificar logs del sistema\n2. Validar configuración\n3. Reiniciar servicios\n\n¿Necesitas más detalles?",
            f"📋 **ANÁLISIS**: He revisado el historial de casos similares. La mayoría se resuelven validando la consistencia de los datos.",
            f"⚡ **RECOMENDACIÓN**: Para esta incidencia, recomiendo:\n- Validar conexiones a base de datos\n- Revisar permisos de usuario\n- Verificar estado de servicios",
            f"📊 **ESTADÍSTICAS**: Según el historial, el 70% de casos similares se resuelven en menos de 2 horas.",
            f"🎯 **PLAN DE ACCIÓN**:\n1. Diagnosticar el problema\n2. Aplicar solución temporal si es posible\n3. Implementar solución definitiva\n4. Documentar el caso",
        ]
        
        import random
        return random.choice(responses)

    def _get_simulated_analysis(self, description: str) -> dict:
        """Análisis simulado para demo"""
        return {
            "title": f"Análisis de incidencia: {description[:30]}...",
            "category": "general",
            "priority": "media",
            "diagnosis": "Posible error de configuración o inconsistencia en datos",
            "solution": """Pasos sugeridos:
1. Revisar logs del sistema
2. Validar configuración actual
3. Verificar integridad de datos
4. Aplicar corrección necesaria
5. Probar solución""",
            "precautions": "Realizar backup antes de aplicar cambios"
        }

ai_service = AIService()