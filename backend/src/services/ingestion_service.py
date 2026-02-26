from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, SparseVectorParams
from openai import AsyncOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from fastembed import SparseTextEmbedding
from ..core.config import settings
import uuid

class IngestionService:
    def __init__(self):
        self.qdrant = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )
        self.openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        
        if settings.ENABLE_HYBRID_SEARCH:
            # Init sparse model (CPU optimized, fast)
            self.sparse_model = SparseTextEmbedding(model_name="Qdrant/bm42-all-minilm-l6-v2-attentions")
            
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        try:
            self._ensure_collection()
        except Exception as e:
            print(f"ERROR: Could not connect to Qdrant at startup: {e}")
            # No lanzamos excepción para que la API pueda arrancar
            # Fallará solo cuando se intente usar Qdrant.

    def _ensure_collection(self):
        try:
            self.qdrant.get_collection(self.collection_name)
        except Exception:
            print(f"Creating collection {self.collection_name} with Hybrid Config...")
            
            vectors_config = {
                "dense": VectorParams(size=1536, distance=Distance.COSINE)
            }
            sparse_vectors_config = None
            
            if settings.ENABLE_HYBRID_SEARCH:
                sparse_vectors_config = {
                    "sparse": SparseVectorParams(
                        index=models.SparseIndexParams(on_disk=False)
                    )
                }
            
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=vectors_config,
                sparse_vectors_config=sparse_vectors_config
            )

        # Crear índices de payload para optimizar filtros
        try:
            self.qdrant.create_payload_index(
                collection_name=self.collection_name,
                field_name="insurer",
                field_schema=models.PayloadSchemaType.KEYWORD
            )
            self.qdrant.create_payload_index(
                collection_name=self.collection_name,
                field_name="document_type",
                field_schema=models.PayloadSchemaType.KEYWORD
            )
            self.qdrant.create_payload_index(
                collection_name=self.collection_name,
                field_name="description",
                field_schema=models.PayloadSchemaType.TEXT
            )
            print("Índices de payload verificados/creados exitosamente.")
        except Exception as e:
            print(f"Advertencia al crear índices: {e}")

    async def get_embedding(self, text: str) -> list[float]:
        text = text.replace("\n", " ")
        response = await self.openai.embeddings.create(
            input=[text],
            model="text-embedding-3-small"
        )
        return response.data[0].embedding

    def get_sparse_vector(self, text: str) -> models.SparseVector:
        # Generate sparse vector
        # list() because embed returns a generator
        sparse_embedding = list(self.sparse_model.embed([text]))[0] 
        return models.SparseVector(
            indices=sparse_embedding.indices.tolist(),
            values=sparse_embedding.values.tolist()
        )

    async def process_document(self, content: str, metadata: dict) -> int:
        """
        Process a document: chunk, embed, and index in Qdrant.
        Returns number of chunks indexed.
        """
        chunks = self.text_splitter.split_text(content)
        points = []
        
        for i, chunk in enumerate(chunks):
            # Dense Vector
            dense_embedding = await self.get_embedding(chunk)
            
            vector_struct = {"dense": dense_embedding}
            
            # Sparse Vector (Optional)
            if settings.ENABLE_HYBRID_SEARCH:
                sparse_vector = self.get_sparse_vector(chunk)
                vector_struct["sparse"] = sparse_vector
            
            # Enrich metadata
            payload = metadata.copy()
            payload["content"] = chunk
            payload["chunk_index"] = i
            payload["total_chunks"] = len(chunks)
            
            points.append(models.PointStruct(
                id=str(uuid.uuid4()),
                vector=vector_struct,
                payload=payload
            ))
            
        if points:
            # Batch upsert
            self.qdrant.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
        return len(points)
