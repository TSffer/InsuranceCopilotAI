from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from ...services.ingestion_service import IngestionService

router = APIRouter()
ingestion_service = IngestionService()

class IngestTextRequest(BaseModel):
    text: str
    metadata: dict = {}

@router.post("/text")
async def ingest_text(request: IngestTextRequest, background_tasks: BackgroundTasks):
    """
    Ingest raw text into Qdrant.
    """
    try:
        # Run in background to avoid blocking
        # But for now let's await to see errors
        count = await ingestion_service.process_document(request.text, request.metadata)
        return {"status": "success", "chunks_indexed": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
