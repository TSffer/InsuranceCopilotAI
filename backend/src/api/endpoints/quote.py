from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...core.database import get_db
from ...domain.schemas import QuoteRequest, QuoteResponse, QuoteCreate
from ...services.quote_service import QuoteService

router = APIRouter()

@router.post("/calculate", response_model=list[QuoteResponse])
async def calculate_quote(request: QuoteRequest, db: AsyncSession = Depends(get_db)):
    """
    Calcula cotizaciones disponibles sin crear una orden final, pero sí registra el intento.
    """
    quote_service = QuoteService(db)
    try:
        quotes = await quote_service.get_quotes(request)
        return quotes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", status_code=201)
async def create_quote_selection(quote_create: QuoteCreate, db: AsyncSession = Depends(get_db)):
    """
    Confirma la selección de una cotización.
    """
    # Aquí deberíamos actualizar el estado de la Quote existente o crear una nueva Order.
    # Por ahora, simplemente retornamos éxito simulado.
    return {"message": "Quote selection saved", "status": "accepted"}
