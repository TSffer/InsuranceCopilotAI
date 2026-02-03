from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pgvector.sqlalchemy import Vector
from ..domain.models import Policy
from ..core.config import settings
from openai import AsyncOpenAI
import json

class RAGService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def get_embedding(self, text: str) -> list[float]:
        response = await self.client.embeddings.create(
            input=text,
            model="text-embedding-3-large"
        )
        return response.data[0].embedding

    async def answer_legal_query(self, query: str) -> str:
        """
        1. Convierte query a vector.
        2. Busca políticas similares en PostgreSQL (pgvector).
        3. Genera respuesta con GPT-4o.
        """
        query_embedding = await self.get_embedding(query)
        
        # Búsqueda Vectorial (L2 Distance / Cosine Similarity implícito en order_by)
        # Usamos el operador <-> para distancia euclidiana (o <=> para coseno si configurado)
        stmt = select(Policy).order_by(Policy.embedding.l2_distance(query_embedding)).limit(3)
        result = await self.db.execute(stmt)
        relevant_docs = result.scalars().all()
        
        if not relevant_docs:
            return "No encontré información relevante en las pólizas cargadas."

        # Construir contexto
        context = "\n\n".join([
            f"--- Póliza: {d.insurer_name} ({d.policy_type}) ---\n{d.content_text[:2000]}..." 
            for d in relevant_docs
        ])

        system_prompt = """Eres un abogado experto en seguros vehiculares. 
        Usa SOLO el contexto proporcionado para responder. 
        Cita la aseguradora y el tipo de plan para cada afirmación.
        Si la información no está en el contexto, di que no lo sabes."""
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Contexto:\n{context}\n\nPregunta: {query}"}
            ]
        )
        
        return response.choices[0].message.content
