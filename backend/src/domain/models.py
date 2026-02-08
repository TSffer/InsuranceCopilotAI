from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from ..core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="viewer")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    threads = relationship("ChatThread", back_populates="user")

class ChatThread(Base):
    __tablename__ = "chat_threads"

    id = Column(String, primary_key=True, index=True) # UUID
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="threads")
    messages = relationship("ChatMessage", back_populates="thread", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, index=True) # UUID
    thread_id = Column(String, ForeignKey("chat_threads.id"))
    role = Column(String) # user, assistant
    content = Column(Text)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    thread = relationship("ChatThread", back_populates="messages")

class Policy(Base):
    """
    Datos estructurados + Datos vectoriales
    """
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    # Metadata Comercial
    insurer_name = Column(String, index=True)
    policy_type = Column(String)
    
    # Tarifario base
    base_price = Column(Float) 
    
    # Contenido para RAG
    content_text = Column(Text)
    embedding = mapped_column(Vector(1536))
    
    metadata_json = Column(JSON)

class Rate(Base):
    """
    Tarifario: Define el precio base según características del vehículo.
    """
    __tablename__ = "rates"

    id = Column(Integer, primary_key=True, index=True)
    insurer = Column(String, index=True)      # Rimac
    plan_name = Column(String)                # Todo Riesgo
    
    # Factores de riesgo
    brand = Column(String, index=True)        # Toyota
    model = Column(String, index=True)        # Corolla
    year_min = Column(Integer)                # 2020
    year_max = Column(Integer)                # 2025
    usage = Column(String)                    # Particular, Taxi
    
    base_price = Column(Float)                # 500.00
    variable_rate = Column(Float)             # 0.03

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    dni = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    phone = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    quotes = relationship("Quote", back_populates="customer")

class Quote(Base):
    """
    Historial de Cotizaciones Realizadas
    """
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relación con Cliente
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    
    # Datos del Input
    customer_age = Column(Integer)
    car_brand = Column(String) 
    car_model = Column(String)
    car_type = Column(String)
    car_usage = Column(String)
    car_year = Column(Integer)
    
    # Resultado
    selected_insurer = Column(String)
    selected_plan = Column(String)
    final_price = Column(Float)
    status = Column(String, default="pending")  # pending, accepted, rejected
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User")
    customer = relationship("Customer", back_populates="quotes")
