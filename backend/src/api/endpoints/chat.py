from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ...core.database import get_db
from ...domain.schemas import ChatRequest, ChatResponse, QuoteRequest, QuoteResponse, ThreadResponse, ThreadCreate, ThreadUpdate, MessageResponse
from ...services.agent_service import AgentService, QuoteService
from ...services.chat_service import ChatService
from ..deps import get_current_user
from ...domain.models import User

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Endpoint inteligente unificado.
    """
    try:
        agent_service = AgentService(db)
        result = await agent_service.process_query(request.message, current_user.id, request.thread_id)
        
        return ChatResponse(
            answer=str(result["answer"]),
            thread_id=result["thread_id"],
            sources=["Agent Generated"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Thread Management ---

@router.get("/threads", response_model=List[ThreadResponse])
async def list_threads(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_id = current_user.id 
    chat_service = ChatService(db)
    return await chat_service.get_user_threads(user_id)

@router.post("/threads", response_model=ThreadResponse)
async def create_thread(thread: ThreadCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_id = current_user.id
    chat_service = ChatService(db)
    return await chat_service.create_thread(user_id, thread.title)

@router.put("/threads/{thread_id}", response_model=ThreadResponse)
async def update_thread(thread_id: str, thread_update: ThreadUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_id = current_user.id
    chat_service = ChatService(db)
    updated = await chat_service.update_thread(thread_id, user_id, thread_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Thread not found")
    return updated

@router.delete("/threads/{thread_id}")
async def delete_thread(thread_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_id = current_user.id
    chat_service = ChatService(db)
    success = await chat_service.delete_thread(thread_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Thread not found")
    return {"status": "success"}

@router.get("/threads/{thread_id}/messages", response_model=List[MessageResponse])
async def get_messages(thread_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    chat_service = ChatService(db)
    return await chat_service.get_thread_messages(thread_id)

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
