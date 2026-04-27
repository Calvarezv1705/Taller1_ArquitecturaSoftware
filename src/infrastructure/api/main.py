"""Punto de entrada de la API REST con FastAPI."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from src.application.chat_service import ChatService
from src.application.dtos import ChatHistoryDTO, ChatMessageRequestDTO, ChatMessageResponseDTO, ProductDTO
from src.application.product_service import ProductService
from src.config import settings
from src.domain.exceptions import ChatServiceError, ProductNotFoundError
from src.infrastructure.db.database import get_db, init_db
from src.infrastructure.llm_providers.gemini_service import GeminiService
from src.infrastructure.repositories.chat_repository import SQLChatRepository
from src.infrastructure.repositories.product_repository import SQLProductRepository

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API de e-commerce de zapatos con chat inteligente usando Clean Architecture.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    """Inicializa la base de datos al iniciar la aplicación."""
    init_db()


@app.get("/")
def root() -> dict:
    """Retorna metadatos básicos de la API."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/products", response_model=list[ProductDTO])
def get_products(
    brand: str | None = Query(default=None, description="Filtro opcional por marca"),
    category: str | None = Query(default=None, description="Filtro opcional por categoría"),
    db: Session = Depends(get_db),
) -> list[ProductDTO]:
    """Lista productos y permite filtros opcionales por marca/categoría."""
    product_service = ProductService(SQLProductRepository(db))
    return product_service.search_products(brand=brand, category=category)


@app.get("/products/{product_id}", response_model=ProductDTO)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)) -> ProductDTO:
    """Obtiene un producto por su identificador."""
    product_service = ProductService(SQLProductRepository(db))
    try:
        return product_service.get_product_by_id(product_id)
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/chat", response_model=ChatMessageResponseDTO)
async def chat(request: ChatMessageRequestDTO, db: Session = Depends(get_db)) -> ChatMessageResponseDTO:
    """Procesa un mensaje de chat y retorna respuesta del asistente IA."""
    product_repo = SQLProductRepository(db)
    chat_repo = SQLChatRepository(db)
    try:
        ai_service = GeminiService()
        chat_service = ChatService(product_repo, chat_repo, ai_service)
        return await chat_service.process_message(request)
    except ChatServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/chat/history/{session_id}", response_model=list[ChatHistoryDTO])
def get_chat_history(
    session_id: str,
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[ChatHistoryDTO]:
    """Retorna historial de una sesión de chat."""
    chat_service = ChatService(SQLProductRepository(db), SQLChatRepository(db))
    return chat_service.get_session_history(session_id=session_id, limit=limit)


@app.delete("/chat/history/{session_id}")
def delete_chat_history(session_id: str, db: Session = Depends(get_db)) -> dict:
    """Elimina todos los mensajes de una sesión y retorna contador."""
    chat_service = ChatService(SQLProductRepository(db), SQLChatRepository(db))
    deleted_count = chat_service.clear_session_history(session_id=session_id)
    return {
        "session_id": session_id,
        "deleted_messages": deleted_count,
    }


@app.get("/health")
def health_check() -> dict:
    """Endpoint de verificación de salud del servicio."""
    return {
        "status": "ok",
        "timestamp": datetime.now(UTC).isoformat(),
    }
