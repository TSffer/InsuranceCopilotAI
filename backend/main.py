import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.core.config import settings
from src.core.database import engine, Base
from src.api.endpoints import chat

from sqlalchemy import text

# Lifecycle event to initialize DB (dev only)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Step 1: Extension 'vector' removed (using Qdrant)
    loop = asyncio.get_running_loop()

    # Initialize Checkpointer (AsyncPostgresSaver)
    from src.services.agent_service import initialize_checkpointer
    try:
        await initialize_checkpointer()
    except Exception as e:
        print(f"ERROR: Could not initialize checkpointer: {e}")
        # We might want to raise here if it's critical, or just log
        # raise e

    # Step 2: Create tables
    # In production we would use Alembic for migrations.
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Uncomment to reset
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

from src.api.endpoints import chat, auth, ingest, quote

from fastapi.middleware.cors import CORSMiddleware

# Routers
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(chat.router, prefix=settings.API_V1_STR, tags=["chat"])
app.include_router(ingest.router, prefix=f"{settings.API_V1_STR}/ingest", tags=["ingestion"])
app.include_router(quote.router, prefix=f"{settings.API_V1_STR}/quotes", tags=["quotes"])
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])

# CORS Configuration
origins = [
    "http://localhost:4200",
    "http://localhost",
    "http://127.0.0.1:4200",
]

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
