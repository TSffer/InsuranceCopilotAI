from typing import List, Any
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.prebuilt import create_react_agent
from ..services.quote_service import QuoteService
from ..services.rag_service import RAGService
from ..services.chat_service import ChatService
from ..domain.schemas import QuoteRequest
from ..core.config import settings

# Global checkpointer variables
# Pool and saver are initialized lazily
_pool: AsyncConnectionPool = None
_checkpointer: AsyncPostgresSaver = None

class AgentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm = ChatOpenAI(
            model="gpt-4o", 
            temperature=0, 
            api_key=settings.OPENAI_API_KEY
        )
        
        # Instanciar servicios base
        self.quote_service = QuoteService(db)
        self.rag_service = RAGService(db)
        self.chat_service = ChatService(db)

    async def get_checkpointer(self):
        """
        Singleton lazy initialization of AsyncPostgresSaver.
        Ensures setup() is called once to create tables.
        """
        global _pool, _checkpointer
        if _pool is None:
            # PostgresSaver needs autocommit=True for the initial setup (migrations)
            # because some operations (like CREATE INDEX CONCURRENTLY) cannot run in a transaction block.
            _pool = AsyncConnectionPool(
                conninfo=settings.POSTGRES_CONNECTION_URI, 
                open=False,
                kwargs={"autocommit": True}
            )
            await _pool.open()
            
        if _checkpointer is None:
            _checkpointer = AsyncPostgresSaver(_pool)
            await _checkpointer.setup()
            
        return _checkpointer

    async def get_executor(self) -> Any:
        # 0. Obtener Checkpointer
        checkpointer = await self.get_checkpointer()

        # 1. Definir Tools (re-defining here to ensure they are in scope)
        @tool
        async def calculate_insurance_quote(age: int, car_brand: str, car_model: str, car_year: int, dni: str = None, first_name: str = None, usage: str = "Particular") -> str:
            """
            Útil SOLO cuando el usuario quiere saber el PRECIO, costo o cotización de un seguro.
            Calcula la prima exacta para un auto específico.
            Requiere: edad conductor, MARCA y MODELO del auto (ej: Toyota Corolla), año fabricación.
            OPCIONAL: DNI y Nombre para guardar el cliente.
            """
            try:
                # Convertir a Pydantic
                req = QuoteRequest(age=age, car_brand=car_brand, car_model=car_model, car_year=car_year, usage=usage, dni=dni, first_name=first_name)
                # Llamar al servicio determinista
                quotes = await self.quote_service.get_quotes(req)
                
                # Formatear respuesta para el LLM
                if not quotes:
                    return "No se encontraron cotizaciones para ese perfil."
                    
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
            Ejemplo: '¿Cubre robo de espejos?', '¿Qué pasa si manejo ebrio?', 'Comparar deducibles'.
            NO usar para precios numéricos.
            """
            return await self.rag_service.answer_legal_query(query)

        tools = [calculate_insurance_quote, search_legal_conditions]
        
        # 2. Definir Prompt
        system_prompt = """Eres el Copiloto de Seguros Inteligente.
            Tu misión es ayudar al usuario usando las herramientas disponibles.
            
            REGLAS:
            - Si el usuario saluda, responde amablemente.
            - Si pide PRECIO, usa 'calculate_insurance_quote'. Si faltan datos (edad, auto), PREGUNTALOS antes de llamar a la herramienta.
            - Si pregunta CONDICIONES, usa 'search_legal_conditions'.
            - Si pregunta AMBAS cosas, usa AMBAS herramientas.
            """

        # 3. Crear Agente LangGraph
        # Version 0.1.7 signature: (model, tools, *, prompt=None, ...)
        agent = create_react_agent(self.llm, tools, prompt=system_prompt, checkpointer=checkpointer)
        return agent

    async def process_query(self, user_query: str, thread_id: str = None) -> dict:
        """
        Punto de entrada principal.
        Retorna tanto la respuesta como el thread_id usado.
        """
        # 1. Thread Management & User Message Persistence
        if not thread_id:
            # Create new thread logic. Assuming a default user_id or system user for now.
            # Ideally, user_id comes from context/auth.
            user_id = 1 # Placeholder/Default user
            thread = await self.chat_service.create_thread(user_id, "Nueva Conversación")
            thread_id = thread.id
        
        # Save User Message
        await self.chat_service.save_message(thread_id, "user", user_query)

        # 2. Agent Execution
        checkpointer = await self.get_checkpointer() # Ensure checkpointer initialized
        agent_graph = await self.get_executor()
        
        config = {"configurable": {"thread_id": thread_id}}
        inputs = {"messages": [("user", user_query)]}
        
        # Invoke agent
        result = await agent_graph.ainvoke(inputs, config=config)
        
        # 3. Agent Response Persistence
        messages = result["messages"]
        last_message = messages[-1]
        answer_content = last_message.content
        
        await self.chat_service.save_message(thread_id, "assistant", answer_content)

        return {
            "answer": answer_content,
            "thread_id": thread_id
        }
