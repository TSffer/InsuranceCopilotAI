from qdrant_client import QdrantClient
from qdrant_client.http import models
from openai import AsyncOpenAI
from flashrank import Ranker, RerankRequest
from fastembed import SparseTextEmbedding
from ..core.config import settings
import asyncio


_qdrant_client = None
_ranker = None
_sparse_model = None

class RAGService:
    def __init__(self):
        global _qdrant_client, _ranker, _sparse_model
        
        # Inicializar Qdrant
        if _qdrant_client is None:
            _qdrant_client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY
            )
        self.qdrant = _qdrant_client
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        
        # Inicializar LLM
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Inicializar Reranker (Once)
        if settings.ENABLE_RERANKING and _ranker is None:
            _ranker = Ranker(model_name=settings.RERANK_MODEL, cache_dir="/tmp/flashrank")
        self.ranker = _ranker
            
        # Inicializar Sparse Model (Once)
        if settings.ENABLE_HYBRID_SEARCH and _sparse_model is None:
            _sparse_model = SparseTextEmbedding(model_name="Qdrant/bm42-all-minilm-l6-v2-attentions")
        self.sparse_model = _sparse_model

    async def get_embedding(self, text: str) -> list[float]:
        text = text.replace("\n", " ")
        response = await self.client.embeddings.create(
            input=[text],
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
        
    def get_sparse_vector(self, text: str) -> models.SparseVector:
        sparse_embedding = list(self.sparse_model.embed([text]))[0]
        return models.SparseVector(
            indices=sparse_embedding.indices.tolist(),
            values=sparse_embedding.values.tolist()
        )

    async def expand_query(self, query: str) -> list[str]:
        if not settings.ENABLE_QUERY_EXPANSION:
            return [query]
            
        system_prompt = """Eres un experto en seguros. Genera 3 variantes de búsqueda (sinónimos, términos técnicos) para la consulta del usuario.
        Responde SOLO con las variantes separadas por '||'. Ejemplo: 'Robo espejo||Hurto parcial||Cobertura accesorios'"""
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.5
            )
            content = response.choices[0].message.content
            variants = [v.strip() for v in content.split("||")]
            return [query] + variants
        except Exception:
            return [query]

    async def retrieve_documents(self, queries: list[str], limit: int = 10) -> list[dict]:
        all_docs = {}
        
        for q in queries:
            dense_vector = await self.get_embedding(q)
            
            if settings.ENABLE_HYBRID_SEARCH:
                sparse_vector = self.get_sparse_vector(q)
                
                results = self.qdrant.query_points(
                    collection_name=self.collection_name,
                    prefetch=[
                        models.Prefetch(
                            query=sparse_vector,
                            using="sparse",
                            limit=limit * 2, 
                        )
                    ],
                    query=dense_vector,
                    using="dense",
                    limit=limit,
                    with_payload=True
                ).points
                
            else:
                results = self.qdrant.query_points(
                    collection_name=self.collection_name,
                    query=dense_vector,
                    limit=limit
                ).points

            for res in results:
                if res.payload:
                     doc_id = res.id 
                     if doc_id not in all_docs or res.score > all_docs[doc_id]['score']:
                         all_docs[doc_id] = {
                             "id": doc_id,
                             "content": res.payload.get("content", ""),
                             "metadata": res.payload,
                             "score": res.score
                         }
        
        return list(all_docs.values())

    async def rerank_documents(self, query: str, docs: list[dict]) -> list[dict]:
        if not settings.ENABLE_RERANKING or not docs:
            return docs
            
        passages = [
            {"id": str(d["id"]), "text": d["content"], "meta": d["metadata"]} 
            for d in docs
        ]
        
        rerank_request = RerankRequest(query=query, passages=passages)
        results = self.ranker.rerank(rerank_request)
        
        reranked_docs = []
        for res in results:
            reranked_docs.append({
                "id": res["id"],
                "content": res["text"],
                "metadata": res["meta"],
                "score": res["score"]
            })
            
        return reranked_docs

    async def answer_legal_query(self, query: str, force_table: bool = False) -> dict:
        # Pipeline ejecución
        queries = await self.expand_query(query)
        docs = await self.retrieve_documents(queries)
        
        if settings.ENABLE_RERANKING:
            docs = await self.rerank_documents(query, docs)
            docs = docs[:5] 
            
        if not docs:
            return {"answer": "No encontré información relevante en las pólizas cargadas.", "sources": []}

        context = "\n\n".join([
            f"--- Doc: {d.get('metadata', {}).get('source_file')} ---\n{d['content']}" 
            for d in docs
        ])
        
        unique_sources_map = {}
        for d in docs:
            fname = d.get('metadata', {}).get('source_file', 'Unknown')
            if fname not in unique_sources_map:
                unique_sources_map[fname] = {
                    "title": fname,
                    "content": d['content'],
                    "id": str(d.get("id", "")),
                    "score": float(d.get("score")) if d.get("score") is not None else None
                }
        
        rich_sources = list(unique_sources_map.values())

        system_prompt = """Eres un experto en seguros. Responde usando SOLO el contexto proporcionado.
        - Resalta montos, porcentajes y monedas (USD, Soles).
        - Cita la fuente del documento (ej: "Según Plan Km...").
        """

        if force_table:
            system_prompt += """
            - LA RESPUESTA DEBE SER EXCLUSIVAMENTE UNA TABLA MARKDOWN DETALLADA.
            - Columnas sugeridas: 'Aseguradora/Plan', 'Cobertura Principal', 'Deducible', 'Exclusiones', 'Beneficios Extra'.
            - NO uses listas con viñetas fuera de la tabla.
            - NO uses párrafos introductorios ni conclusivos.
            - Formato MARKDOWN puro.
            """
        
        user_content = f"Contexto:\n{context}\n\nPregunta: {query}"
        if force_table:
            user_content += "\n\nGENERAR TABLA COMPARATIVA MARKDOWN DETALLADA."

        response = await self.client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=settings.LLM_TEMPERATURE
        )
        
        return {
            "answer": response.choices[0].message.content,
            "sources": rich_sources
        }
