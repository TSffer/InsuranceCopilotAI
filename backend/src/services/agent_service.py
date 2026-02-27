from typing import List, Any, Tuple
import uuid
import json
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import ToolMessage 

from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.prebuilt import create_react_agent
from ..services.quote_service import QuoteService
from ..services.rag_service import RAGService
from ..services.chat_service import ChatService
from ..domain.schemas import QuoteRequest
from ..core.config import settings
from ..services.semantic_router import SemanticRouter

# Global checkpointer variables
_pool: AsyncConnectionPool = None
_checkpointer: AsyncPostgresSaver = None


async def initialize_checkpointer():
    global _pool, _checkpointer
    if _pool is None:
        try:
            _pool = AsyncConnectionPool(
                conninfo=settings.POSTGRES_CONNECTION_URI, 
                open=False,
                kwargs={"autocommit": True}
            )
            await _pool.open()
        except Exception as e:
            # print(f"DEBUG: Error opening pool: {e}")
            raise e
        
    if _checkpointer is None:
        _checkpointer = AsyncPostgresSaver(_pool)
        await _checkpointer.setup()
        
    return _checkpointer

class AgentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL, 
            temperature=settings.LLM_TEMPERATURE, 
            api_key=settings.OPENAI_API_KEY
        )
        
        # Instanciar servicios base
        self.quote_service = QuoteService(db)
        self.rag_service = RAGService()
        self.chat_service = ChatService(db)

    async def get_checkpointer(self):
        return await initialize_checkpointer()

    async def get_executor(self) -> Any:
        # 0. Obtener Checkpointer (Persistencia)
        checkpointer = await self.get_checkpointer()

        # 1. Definir Tools
        
        @tool
        async def calculate_insurance_quote(age: int, car_brand: str, car_model: str, car_year: int, dni: str = None, first_name: str = None, usage: str = "Particular") -> str:
            """
            Útil SOLO cuando el usuario quiere saber el PRECIO, costo o cotización de un seguro.
            Calcula la prima exacta para un auto específico.
            
            REQUIERE OBLIGATORIAMENTE:
            - age (edad del conductor)
            - car_brand (Marca: Toyota, Nissan, Kia, etc.)
            - car_model (Modelo: Corolla, Yaris, Rio, etc.)
            - car_year (Año de fabricación: 2020, 2023, etc.)
            
            OPCIONALES:
            - usage (Uso: 'Particular', 'Taxi', 'Carga', 'Comercial'). Si no se especifica, asumir 'Particular'.
            - dni y first_name (Datos del cliente).
            
            SI FALTAN DATOS (especialmente Marca, Modelo o Año), NO INVENTES. PREGUNTA al usuario por el dato que falta.
            """
            try:
                # Convertir argumentos a esquema Pydantic para el servicio
                req = QuoteRequest(age=age, car_brand=car_brand, car_model=car_model, car_year=car_year, usage=usage, dni=dni, first_name=first_name)
                # Llamar al servicio de cotización
                quotes = await self.quote_service.get_quotes(req)
                
                # Formatear respuesta para el LLM
                if not quotes:
                    return "No se encontraron cotizaciones para ese perfil en nuestra base de datos."
                    
                response_str = "Cotizaciones encontradas:\n"
                for q in quotes:
                    response_str += f"- {q.insurer} ({q.plan_name}): ${q.price} ({q.coverage_summary})\n"
                return response_str
            except Exception as e:
                return f"Error calculando cotización: {str(e)}"

        @tool
        async def search_legal_conditions(query: str) -> str:
            """
            Útil cuando el usuario pregunta sobre COBERTURAS, condiciones, exclusiones, o cláusulas legales.
            Ejemplo: '¿Cubre robo de espejos?', '¿Qué pasa si manejo ebrio?'.
            Busca en la documentación legal y pólizas.
            """
            result = await self.rag_service.answer_legal_query(query)
            return json.dumps(result, ensure_ascii=False)

        @tool
        async def compare_insurance_policies(query: str) -> str:
            """
            Útil cuando el usuario pide COMPARAR dos o más planes/aseguradoras.
            También si pide 'coberturas de X, Y y Z'.
            Ejemplo: 'Diferencia entre Rimac y Pacífico', 'Comparar deducibles', 'Coberturas de Rimac y Mapfre'.
            Genera una TABLA COMPARATIVA basándose en la documentación legal.
            """
            result = await self.rag_service.answer_legal_query(query, force_table=True)
            return json.dumps(result, ensure_ascii=False)

        tools = [calculate_insurance_quote, search_legal_conditions, compare_insurance_policies]
        
        # 2. Definir Prompt del Sistema (System Prompt)
        system_prompt = """Eres el Copiloto de Seguros Inteligente.
            Tu misión es ayudar al usuario usando las herramientas disponibles de manera eficiente.
            
            REGLAS:
            - Responde SIEMPRE en español de forma amable y profesional.
            - Si el usuario pide PRECIO/COTIZACIÓN, usa 'calculate_insurance_quote'. Si te faltan datos (edad, marca, modelo, año), PÍDELOS amablemente antes de llamar a la herramienta.
            - Si el usuario pregunta por COBERTURAS o condiciones generales, usa 'search_legal_conditions'.
            - Si el usuario pide una COMPARACIÓN entre aseguradoras o planes, usa 'compare_insurance_policies'.
            - Si la pregunta es compleja y requiere ambos (precios y condiciones), puedes usar múltiples herramientas.
            """

        # 3. Crear Agente con LangGraph
        agent = create_react_agent(self.llm, tools, prompt=system_prompt, checkpointer=checkpointer)
        return agent

    async def process_query(self, user_query: str, user_id: int, thread_id: str = None) -> dict:
        """
        Punto de entrada principal.
        Maneja el enrutamiento semántico (Saludos/Seguridad) y ejecuta el Agente para consultas complejas.
        """
        # 1. Gestión de Hilos (Threads)
        if not thread_id:
            thread = await self.chat_service.create_thread(user_id, "Nueva Conversación")
            thread_id = thread.id
            
        # 2. Enrutamiento Semántico (Optimización y Seguridad)
        router = SemanticRouter()
        route = await router.route(user_query)
        
        # Respuesta rápida para Seguridad
        if route == "UNSAFE":
            response = "Lo siento, no puedo procesar esa solicitud por razones de seguridad."
            await self._save_interaction(thread_id, user_query, response)
            return {"answer": response, "thread_id": thread_id}
            
        # Respuesta rápida para Saludos
        if route == "GREETING":
            response = "¡Hola! Soy tu Copiloto de Seguros. ¿En qué te puedo ayudar hoy? Puedo cotizar seguros (necesito datos de tu auto), comparar opciones o resolver dudas sobre coberturas."
            await self._save_interaction(thread_id, user_query, response)
            return {"answer": response, "thread_id": thread_id}

        # 3. Ejecución del Agente para consultas de negocio (Quote, Comparison, Info)
        executor = await self.get_executor()
        
        inputs = {"messages": [("user", user_query)]}
        config = {"configurable": {"thread_id": thread_id}}
        
        # Invocamos al agente
        result = await executor.ainvoke(inputs, config=config)
        
        # Extraemos el último mensaje del asistente
        assistant_response = result["messages"][-1].content
        
        # Extraer sources de los ToolMessages 
        unique_sources = {}
        for msg in result["messages"]:
            if isinstance(msg, ToolMessage):
                try:
                    data = json.loads(msg.content)
                    if isinstance(data, dict) and "sources" in data:
                        for s in data["sources"]:
                             if isinstance(s, dict) and "title" in s:
                                unique_sources[s["title"]] = s
                except:
                    pass
                            
        # 4. Guardar Interacción
        sources_list = list(unique_sources.values()) if unique_sources else []
        await self._save_interaction(thread_id, user_query, assistant_response, sources_list)

        return {
            "answer": assistant_response,
            "thread_id": thread_id,
            "sources": list(unique_sources.values()) if unique_sources else []
        }

    async def _save_interaction(self, thread_id: str, user_msg: str, assistant_msg: str, sources: List[dict] = None):
        """Método auxiliar para guardar el historial de chat en la base de datos."""
        await self.chat_service.save_message(thread_id, "user", user_msg)
        
        metadata = None
        if sources:
            metadata = {"sources": sources}
            
        await self.chat_service.save_message(thread_id, "assistant", assistant_msg, metadata=metadata)
