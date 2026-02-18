from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Literal

from ...services.semantic_router import SemanticRouter

router = APIRouter()
semantic_router = SemanticRouter()

class AnchorCreate(BaseModel):
    text: str
    type: Literal["GREETING", "UNSAFE"]

class AnchorResponse(BaseModel):
    text: str
    type: str

@router.get("/anchors", response_model=List[AnchorResponse])
async def list_anchors():
    """
    List all semantic anchors (greetings, unsafe inputs) stored in Qdrant.
    """
    try:
        return await semantic_router.list_anchors()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/anchors", response_model=AnchorResponse)
async def add_anchor(anchor: AnchorCreate):
    """
    Add a new semantic anchor.
    """
    try:
        await semantic_router.add_anchor(anchor.text, anchor.type)
        return anchor
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/anchors")
async def delete_anchor(text: str = Query(..., description="The exact text of the anchor to delete")):
    """
    Delete an anchor by its text.
    """
    try:
        await semantic_router.delete_anchor(text)
        return {"status": "success", "message": f"Anchor '{text}' deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
