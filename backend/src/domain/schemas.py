from pydantic import BaseModel
from typing import List, Optional, Any

# --- Shared ---
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    email: str
    
class UserCreate(UserBase):
    password: str
    username: Optional[str] = None
    role: str = "viewer"

class UserLogin(UserBase):
    password: str
    
class UserResponse(UserBase):
    id: int
    username: Optional[str] = None
    role: str
    is_active: bool = True

    class Config:
        from_attributes = True

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
    # car_brand, car_model, etc. flattened or nested. 
    # Frontend sends nested 'vehicle'. Let's support nested to match frontend types.ts more closely
    # OR keep it flat. The current QuoteRequest is flat. 
    # Frontend QuoteRequest: vehicle: { brand, model, year, type }
    # Let's align backend to frontend for easier integration.
    vehicle: Optional[dict] = None # Flexible dict for now to avoid validation hell, or define a schema.
    
    # Flattened for backward compatibility if needed, but let's encourage nested
    car_brand: Optional[str] = None
    car_model: Optional[str] = None
    car_year: Optional[int] = None
    usage: str = "Particular"

class QuoteCreate(BaseModel):
    customer_id: Optional[int] = None
    vehicle: dict
    selected_insurer: str
    selected_plan: str
    final_price: float
    status: str = "pending"

class QuoteResponse(BaseModel):
    insurer: str
    plan_name: str
    price: float
    coverage_summary: str

# --- Chat/RAG Schemas ---
from datetime import datetime

# --- Chat/RAG Schemas ---
class ChatRequest(BaseModel):
    # Frontend sends 'message: string'. thread_id optional
    message: str
    thread_id: Optional[str] = None
    
class MessageBase(BaseModel):
    role: str
    content: str
    metadata_json: Optional[Any] = None

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: str
    created_at: datetime
    class Config:
        from_attributes = True

class ThreadBase(BaseModel):
    title: str

class ThreadCreate(ThreadBase):
    pass

class ThreadUpdate(ThreadBase):
    pass

class ThreadResponse(ThreadBase):
    id: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []
    class Config:
        from_attributes = True

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
