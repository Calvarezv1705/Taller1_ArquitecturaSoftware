"""DTOs de la capa de aplicación.

Los *Data Transfer Objects* (DTOs) encapsulan la validación de
entrada/salida para los casos de uso y los endpoints de la API.
Utilizan Pydantic para validación automática de tipos y restricciones.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductDTO(BaseModel):
    """DTO para representar productos en requests y responses.

    Valida que los campos de texto no estén vacíos, que el precio sea
    positivo y que el stock no sea negativo.

    Attributes:
        id (int | None): Identificador del producto. ``None`` al crear uno nuevo.
        name (str): Nombre del producto (1-200 caracteres).
        brand (str): Marca del producto (1-100 caracteres).
        category (str): Categoría del producto (1-100 caracteres).
        size (str): Talla del producto (1-20 caracteres).
        color (str): Color del producto (1-50 caracteres).
        price (float): Precio en dólares, debe ser mayor que 0.
        stock (int): Cantidad en inventario, no puede ser negativo.
        description (str): Descripción opcional del producto.

    Example:
        >>> dto = ProductDTO(
        ...     name="Air Max", brand="Nike", category="Running",
        ...     size="42", color="Negro", price=120.0, stock=5,
        ... )
    """

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
        """Valida que los campos de texto requeridos no estén vacíos.

        Args:
            value (str): Valor del campo a validar.

        Returns:
            str: Valor limpio sin espacios en blanco al inicio/final.

        Raises:
            ValueError: Si el valor está compuesto solo por espacios en blanco.
        """
        if not value.strip():
            raise ValueError("Este campo no puede estar vacío.")
        return value.strip()


class ChatMessageRequestDTO(BaseModel):
    """DTO para recibir mensajes del usuario en el endpoint de chat.

    Attributes:
        session_id (str): Identificador de la sesión del usuario (1-100 caracteres).
        message (str): Texto del mensaje enviado por el usuario.

    Example:
        >>> request = ChatMessageRequestDTO(
        ...     session_id="user123", message="Busco zapatos para correr"
        ... )
    """

    session_id: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1)

    @field_validator("session_id", "message")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        """Valida que ``session_id`` y ``message`` no estén vacíos.

        Args:
            value (str): Valor del campo a validar.

        Returns:
            str: Valor limpio sin espacios en blanco al inicio/final.

        Raises:
            ValueError: Si el valor contiene solo espacios en blanco.
        """
        if not value.strip():
            raise ValueError("El valor no puede estar vacío.")
        return value.strip()


class ChatMessageResponseDTO(BaseModel):
    """DTO para retornar la respuesta del asistente al usuario.

    Attributes:
        session_id (str): Identificador de la sesión.
        user_message (str): Mensaje original del usuario.
        assistant_message (str): Respuesta generada por la IA.
        timestamp (datetime): Marca de tiempo de la respuesta.
    """

    session_id: str
    user_message: str
    assistant_message: str
    timestamp: datetime


class ChatHistoryDTO(BaseModel):
    """DTO para retornar mensajes individuales del historial de chat.

    Attributes:
        id (int | None): Identificador del mensaje en base de datos.
        session_id (str): Identificador de la sesión a la que pertenece.
        role (str): Rol del autor (``'user'`` o ``'assistant'``).
        message (str): Contenido del mensaje.
        timestamp (datetime): Fecha y hora del mensaje.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    session_id: str
    role: str
    message: str
    timestamp: datetime
