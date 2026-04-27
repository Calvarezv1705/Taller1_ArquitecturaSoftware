"""Punto de entrada de la API REST con FastAPI.

Configura la aplicación FastAPI, registra middleware CORS, define
todos los endpoints del e-commerce y del chat con IA, e inicializa
la base de datos al arrancar el servidor.
"""

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
    """Inicializa la base de datos y carga datos semilla al iniciar la aplicación."""
    init_db()


@app.get("/")
def root() -> dict:
    """Retorna metadatos básicos de la API.

    Returns:
        dict: Diccionario con nombre, versión, entorno y rutas útiles.

    Example:
        GET /
        Response: {"name": "E-commerce Chat IA", "version": "1.0.0", ...}
    """
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
    """Obtiene la lista de productos, con filtros opcionales por marca y categoría.

    Este endpoint retorna todos los productos registrados en la base de datos.
    Se pueden aplicar filtros opcionales por marca y/o categoría.

    Args:
        brand (str | None): Filtro opcional por marca (Nike, Adidas, etc.).
        category (str | None): Filtro opcional por categoría (Running, Casual, Formal).
        db (Session): Sesión de base de datos inyectada por FastAPI.

    Returns:
        list[ProductDTO]: Lista de productos con toda su información.

    Example:
        GET /products
        GET /products?brand=Nike
        GET /products?category=Running
        GET /products?brand=Nike&category=Running
    """
    product_service = ProductService(SQLProductRepository(db))
    return product_service.search_products(brand=brand, category=category)


@app.get("/products/{product_id}", response_model=ProductDTO)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)) -> ProductDTO:
    """Obtiene un producto por su identificador único.

    Args:
        product_id (int): Identificador del producto a buscar.
        db (Session): Sesión de base de datos inyectada por FastAPI.

    Returns:
        ProductDTO: Datos completos del producto encontrado.

    Raises:
        HTTPException: Error 404 si el producto no existe.

    Example:
        GET /products/1
        Response: {"id": 1, "name": "Air Zoom Pegasus 40", "price": 120.0, ...}
    """
    product_service = ProductService(SQLProductRepository(db))
    try:
        return product_service.get_product_by_id(product_id)
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/chat", response_model=ChatMessageResponseDTO)
async def chat(request: ChatMessageRequestDTO, db: Session = Depends(get_db)) -> ChatMessageResponseDTO:
    """Procesa un mensaje de chat del usuario y retorna la respuesta del asistente IA.

    El endpoint obtiene el catálogo de productos, recupera el historial
    reciente de la conversación, genera una respuesta con Google Gemini
    y persiste ambos mensajes (usuario y asistente).

    Args:
        request (ChatMessageRequestDTO): Cuerpo del request con ``session_id`` y ``message``.
        db (Session): Sesión de base de datos inyectada por FastAPI.

    Returns:
        ChatMessageResponseDTO: Respuesta con el mensaje del usuario, la respuesta
            del asistente y la marca de tiempo.

    Raises:
        HTTPException: Error 500 si ocurre un fallo al procesar el chat o
            comunicarse con la IA.

    Example:
        POST /chat
        Body: {"session_id": "user123", "message": "Busco zapatos para correr"}
        Response: {"session_id": "user123", "user_message": "...", "assistant_message": "...", ...}
    """
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
    """Retorna el historial de mensajes de una sesión de chat.

    Args:
        session_id (str): Identificador de la sesión a consultar.
        limit (int): Número máximo de mensajes a retornar (1-100). Por defecto 10.
        db (Session): Sesión de base de datos inyectada por FastAPI.

    Returns:
        list[ChatHistoryDTO]: Lista de mensajes en orden cronológico.

    Example:
        GET /chat/history/user123?limit=5
    """
    chat_service = ChatService(SQLProductRepository(db), SQLChatRepository(db))
    return chat_service.get_session_history(session_id=session_id, limit=limit)


@app.delete("/chat/history/{session_id}")
def delete_chat_history(session_id: str, db: Session = Depends(get_db)) -> dict:
    """Elimina todos los mensajes de una sesión y retorna el contador de borrados.

    Args:
        session_id (str): Identificador de la sesión cuyo historial se eliminará.
        db (Session): Sesión de base de datos inyectada por FastAPI.

    Returns:
        dict: Diccionario con ``session_id`` y ``deleted_messages``.

    Example:
        DELETE /chat/history/user123
        Response: {"session_id": "user123", "deleted_messages": 4}
    """
    chat_service = ChatService(SQLProductRepository(db), SQLChatRepository(db))
    deleted_count = chat_service.clear_session_history(session_id=session_id)
    return {
        "session_id": session_id,
        "deleted_messages": deleted_count,
    }


@app.get("/health")
def health_check() -> dict:
    """Endpoint de verificación de salud del servicio.

    Returns:
        dict: Diccionario con ``status`` y ``timestamp`` en formato ISO 8601.

    Example:
        GET /health
        Response: {"status": "ok", "timestamp": "2024-01-15T10:30:00+00:00"}
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(UTC).isoformat(),
    }
