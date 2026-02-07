from pydantic import BaseModel
from typing import List, Optional, Any

# --- Shared ---
class Token(BaseModel):
    access_token: str
    token_type: str

# --- Quote Schemas ---
class QuoteRequest(BaseModel):
    # Datos Cliente
    dni: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    
    # Datos Riesgo
    age: int
    car_brand: str  
    car_model: str
    car_year: int
    usage: str = "Particular"

class QuoteResponse(BaseModel):
    insurer: str
    plan_name: str
    price: float
    coverage_summary: str

# --- Chat/RAG Schemas ---
class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None
    
class ChatResponse(BaseModel):
    answer: str
    thread_id: str
    sources: List[str] = []
    data_table: Optional[Any] = None # Para tablas comparativas

# --- Policy Ingestion ---
class PolicyCreate(BaseModel):
    insurer_name: str
    policy_type: str
    base_price: float
    text_content: str
