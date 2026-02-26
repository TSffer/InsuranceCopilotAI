import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.core.config import settings
from src.core.database import engine, Base
from src.api.endpoints import chat
from src.api.endpoints import files
from src.api.endpoints import chat, auth, ingest

from sqlalchemy import text

# Evento de vida para inicializar DB (dev only)
@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_running_loop()

    # Inicializar Checkpointer (AsyncPostgresSaver)
    from src.services.agent_service import initialize_checkpointer
    from src.services.semantic_router import SemanticRouter
    from src.services.rag_service import RAGService
    try:
        await initialize_checkpointer()
    except Exception as e:
        print(f"WARNING: Could not initialize checkpointer: {e}. Check your POSTGRES_SERVER and POSTGRES_DB variables.")

    # Crear tablas
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            print(f"WARNING: Could not create tables: {e}. Check your database connection parameters.")

    async def prewarm_models():
        print("Pre-warming AI models in background (this might take a few minutes)...")
        try:
            from src.services.semantic_router import SemanticRouter
            from src.services.rag_service import RAGService
            if settings.SEMANTIC_ROUTER_MODE == "semantic":
                SemanticRouter()
            else:
                print("Skipping SemanticRouter model loading (Keyword mode enabled).")
            RAGService()     # Carga Reranker y Sparse embeddings
            print("AI models loaded successfully in background.")
        except Exception as e:
            print(f"WARNING: Could not pre-warm AI models: {e}")

    asyncio.create_task(prewarm_models())

    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Backend is running"}

# Routers
app.include_router(chat.router, prefix=settings.API_V1_STR, tags=["chat"])
app.include_router(ingest.router, prefix=f"{settings.API_V1_STR}/ingest", tags=["ingestion"])
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(files.router, prefix=f"{settings.API_V1_STR}/files", tags=["files"])

# CORS Configuration
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Insurance Copilot V2 API is running", "docs": "/docs"}
