from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse
from ...services.pdf_service import PDFService
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

router = APIRouter()

class PDFRequest(BaseModel):
    title: str
    content: str
    table_data: Optional[List[Dict[str, Any]]] = None

@router.post("/pdf/slip")
async def generate_slip_pdf(request: PDFRequest):
    service = PDFService()
    try:
        buffer = service.generate_slip(request.title, request.content, request.table_data)
        return StreamingResponse(
            buffer, 
            media_type="application/pdf", 
            headers={"Content-Disposition": f"attachment; filename=slip_cotizacion.pdf"}
        )
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
