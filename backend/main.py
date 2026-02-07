from fastapi import FastAPI
from contextlib import asynccontextmanager
from .core.config import settings
from .core.database import engine, Base
from .api.endpoints import chat

from sqlalchemy import text

# Lifecycle event para inicializar DB (solo dev)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Paso 1: Intentar habilitar la extensión vector (en una transacción propia)
    try:
        async with engine.begin() as conn:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            print("INFO: Extension 'vector' enabled/verified.")
    except Exception as e:
        print(f"WARNING: Could not enable 'vector' extension. Ensure your Postgres has pgvector installed. Error: {e}")

    # Paso 2: Crear tablas
    # En producción usaríamos Alembic para migraciones.
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Descomentar para resetear
        try:
            await conn.run_sync(Base.metadata.create_all)
            print("INFO: Tables created successfully.")
        except Exception as e:
            print(f"ERROR: Could not create tables. {e}")
            raise e
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.include_router(chat.router, prefix=settings.API_V1_STR, tags=["chat"])

@app.get("/")
async def root():
    return {"message": "Insurance Copilot V2 API is running", "docs": "/docs"}
