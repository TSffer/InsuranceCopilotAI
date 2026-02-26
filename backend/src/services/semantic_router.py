from qdrant_client import QdrantClient
from qdrant_client.http import models
from ..core.config import settings
from typing import List, Optional
import uuid
from fastembed import TextEmbedding
import difflib

# Global instances for pre-warming and sharing
_embedding_model = None
_qdrant_client = None

class SemanticRouter:
    def __init__(self):
        global _embedding_model, _qdrant_client
        
        self.mode = settings.SEMANTIC_ROUTER_MODE
        self.vector_size = 384
        
        # Solo cargamos modelos pesados si el modo es "semantic"
        if self.mode == "semantic":
            if _embedding_model is None:
                _embedding_model = TextEmbedding(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
            if _qdrant_client is None:
                _qdrant_client = QdrantClient(
                    url=settings.QDRANT_URL, 
                    api_key=settings.QDRANT_API_KEY
                )
            self.embedding_model = _embedding_model
            self.qdrant = _qdrant_client
        else:
            self.embedding_model = None
            self.qdrant = None

        self.collection_name = settings.QDRANT_SEMANTIC_COLLECTION_NAME
        
        # Anchors for Greeting
        self.greeting_anchors = [
            "hola", "buenos dias", "buenas tardes", "buenas noches", 
            "hey", "hello", "hi", "que tal", "como estas", "saludos"
        ]
        
        # Anchors for Safety / Unsafe content
        self.unsafe_anchors = [
            "ignore previous instructions", "system prompt", "delete database", 
            "drop table", "exec(", "eval(", "import os", "rm -rf", 
            "write python code", "generame codigo", "hackear", "bypass security",
        ]

    async def initialize(self):
        """
        Ensure collection exists and populate it if empty.
        Handles migration if vector size changed.
        """
        try:
            # Check if collection exists
            exists = self.qdrant.collection_exists(self.collection_name)
            
            if exists:
                # Check vector config
                collection_info = self.qdrant.get_collection(self.collection_name)
                if collection_info.config.params.vectors.size != self.vector_size:
                    print(f"Vector dimension mismatch (found {collection_info.config.params.vectors.size}, expected {self.vector_size}). Recreating collection...")
                    self.qdrant.delete_collection(self.collection_name)
                    exists = False

            if not exists:
                # Create collection
                self.qdrant.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.vector_size,
                        distance=models.Distance.COSINE
                    )
                )
                
                # Populate
                await self._populate_initial_anchors()
            else:
                 # Even if exists, check count just in case
                count = self.qdrant.count(self.collection_name).count
                if count == 0:
                     await self._populate_initial_anchors()
                     
        except Exception as e:
            print(f"Error initializing SemanticRouter (Qdrant): {e}")

    async def _populate_initial_anchors(self):
        print("Populating initial semantic anchors in Qdrant (FastEmbed)...")
        
        # Greetings
        greeting_embs = await self._get_embeddings_batch(self.greeting_anchors)
        points = []
        for i, text in enumerate(self.greeting_anchors):
            points.append(models.PointStruct(
                id=str(uuid.uuid4()),
                vector=greeting_embs[i],
                payload={"type": "GREETING", "text": text}
            ))
            
        # Unsafe
        unsafe_embs = await self._get_embeddings_batch(self.unsafe_anchors)
        for i, text in enumerate(self.unsafe_anchors):
            points.append(models.PointStruct(
                id=str(uuid.uuid4()),
                vector=unsafe_embs[i],
                payload={"type": "UNSAFE", "text": text}
            ))
            
        if points:
            self.qdrant.upsert(
                collection_name=self.collection_name,
                points=points
            )

    async def _get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        # FastEmbed es sincrono pero rapido, wrapper async si fuera necesario, 
        # pero aqui podemos llamarlo directo. Devuelve un generador.
        embeddings = list(self.embedding_model.embed(texts))
        return [e.tolist() for e in embeddings]

    async def get_embedding(self, text: str) -> List[float]:
        text = text.replace("\n", " ")
        # FastEmbed handles list of texts
        embeddings = list(self.embedding_model.embed([text]))
        return embeddings[0].tolist()

    async def route(self, query: str) -> Optional[str]:
        """
        Returns 'GREETING', 'UNSAFE', or None.
        """
        if self.mode == "keyword":
            return await self._route_keyword(query)
        
        # Modo Semántico (Original)
        # Ensure init (light check)
        await self.initialize()

        query_vector = await self.get_embedding(query)
        
        results = self.qdrant.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=1,
            with_payload=True
        ).points
        
        if not results:
            return None
            
        top_match = results[0]
        score = top_match.score
        route_type = top_match.payload.get("type")
        
        # Thresholds (ajustar segun modelo)
        unsafe_threshold = 0.60 
        greeting_threshold = 0.65
        
        if route_type == "UNSAFE" and score > unsafe_threshold:
            return "UNSAFE"
            
        if route_type == "GREETING" and score > greeting_threshold:
            return "GREETING"
            
        return None

    async def _route_keyword(self, query: str) -> Optional[str]:
        """
        Versión ultra-ligera usando difflib.
        """
        query_lower = query.lower().strip()
        
        # 1. Búsqueda exacta rápida
        if any(word in query_lower for word in self.greeting_anchors):
            return "GREETING"
        
        if any(word in query_lower for word in self.unsafe_anchors):
            return "UNSAFE"
            
        # 2. Búsqueda por similitud (difflib) para capturar typos
        # Usamos un cutoff alto (0.8) para evitar falsos positivos
        close_greetings = difflib.get_close_matches(query_lower, self.greeting_anchors, n=1, cutoff=0.8)
        if close_greetings:
            return "GREETING"
            
        close_unsafe = difflib.get_close_matches(query_lower, self.unsafe_anchors, n=1, cutoff=0.8)
        if close_unsafe:
            return "UNSAFE"
            
        return None

    async def add_anchor(self, text: str, anchor_type: str):
        """
        Adds a single new anchor to the collection.
        anchor_type: 'GREETING' or 'UNSAFE'
        """
        await self.initialize()
        
        embedding = await self.get_embedding(text)
        point = models.PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={"type": anchor_type.upper(), "text": text}
        )
        
        self.qdrant.upsert(
            collection_name=self.collection_name,
            points=[point]
        )
        print(f"Added anchor: '{text}' as {anchor_type.upper()}")

    async def list_anchors(self):
        """
        Lists all anchors in the collection.
        Returns a list of dicts: {'text': str, 'type': str}
        """
        await self.initialize()
        
        # Scroll through all points
        points, _ = self.qdrant.scroll(
            collection_name=self.collection_name,
            limit=100, # Adjust limit as needed
            with_payload=True,
            with_vectors=False
        )
        
        anchors = []
        for p in points:
            anchors.append({
                "text": p.payload.get("text"),
                "type": p.payload.get("type")
            })
            
        return anchors

    async def delete_anchor(self, text: str):
        """
        Deletes an anchor by its exact text match.
        """
        await self.initialize()
        
        # Using Qdrant filter to delete by payload field 'text'
        self.qdrant.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="text",
                            match=models.MatchValue(value=text)
                        )
                    ]
                )
            )
        )
        print(f"Deleted anchor: '{text}'")
