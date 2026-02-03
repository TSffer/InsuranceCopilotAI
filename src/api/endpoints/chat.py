from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...domain.schemas import ChatRequest, ChatResponse, QuoteRequest, QuoteResponse
from ...services.agent_service import AgentService, QuoteService

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Endpoint inteligente unificado.
    El Agente decidirá si cotizar, buscar info legal, o ambas.
    """
    try:
        agent_service = AgentService(db)
        # Pasamos thread_id (opcional)
        result = await agent_service.process_query(request.message, request.thread_id)
        
        return ChatResponse(
            answer=result["answer"],
            thread_id=result["thread_id"],
            sources=["Agent Generated"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quote", response_model=list[QuoteResponse])
async def quote_endpoint(request: QuoteRequest, db: AsyncSession = Depends(get_db)):
    """
    Endpoint directo para cotizar.
    """
    quote_service = QuoteService(db)
    try:
        quotes = await quote_service.get_quotes(request)
        return quotes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
