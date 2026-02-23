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
    try:
        await initialize_checkpointer()
    except Exception as e:
        print(f"ERROR: Could not initialize checkpointer: {e}")
        # We might want to raise here if it's critical, or just log
        # raise e

    # Crear tablas
    # En producción usamos Alembic para migraciones.
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Descomentar para resetear
        try:
            await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            print(f"ERROR: Could not create tables. {e}")
            raise e
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Routers
app.include_router(chat.router, prefix=settings.API_V1_STR, tags=["chat"])
app.include_router(ingest.router, prefix=f"{settings.API_V1_STR}/ingest", tags=["ingestion"])
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(files.router, prefix=f"{settings.API_V1_STR}/files", tags=["files"])

# CORS Configuration
# Para producción en Azure, permitimos todos los orígenes temporalmente
# o puedes añadir la URL de tu Static Web App aquí.
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
