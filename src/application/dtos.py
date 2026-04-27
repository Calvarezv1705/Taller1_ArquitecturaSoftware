"""DTOs de la capa de aplicación.

Contienen validación de entrada/salida para casos de uso y API.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductDTO(BaseModel):
    """DTO para representar productos en requests y responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    name: str = Field(..., min_length=1, max_length=200)
    brand: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=100)
    size: str = Field(..., min_length=1, max_length=20)
    color: str = Field(..., min_length=1, max_length=50)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    description: str = ""

    @field_validator("name", "brand", "category", "size", "color")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        """Valida que los campos de texto requeridos no estén vacíos."""
        if not value.strip():
            raise ValueError("Este campo no puede estar vacío.")
        return value.strip()


class ChatMessageRequestDTO(BaseModel):
    """DTO para recibir mensajes del usuario."""

    session_id: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1)

    @field_validator("session_id", "message")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        """Valida que `session_id` y `message` no estén vacíos."""
        if not value.strip():
            raise ValueError("El valor no puede estar vacío.")
        return value.strip()


class ChatMessageResponseDTO(BaseModel):
    """DTO para retornar la respuesta del asistente."""

    session_id: str
    user_message: str
    assistant_message: str
    timestamp: datetime


class ChatHistoryDTO(BaseModel):
    """DTO para retornar mensajes de historial de chat."""

    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    session_id: str
    role: str
    message: str
    timestamp: datetime
