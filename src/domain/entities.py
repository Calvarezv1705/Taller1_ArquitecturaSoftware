"""Entidades y objetos de valor del dominio.

Este módulo contiene el núcleo de reglas de negocio para productos y chat.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Sequence


@dataclass
class Product:
    """Entidad de dominio que representa un producto del e-commerce."""

    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str = ""
    id: int | None = None

    def __post_init__(self) -> None:
        """Valida las reglas de negocio al crear la entidad."""
        if not self.name or not self.name.strip():
            raise ValueError("El nombre del producto no puede estar vacío.")
        if self.price <= 0:
            raise ValueError("El precio debe ser mayor que cero.")
        if self.stock < 0:
            raise ValueError("El stock no puede ser negativo.")

    def is_available(self) -> bool:
        """Indica si el producto está disponible para la venta.

        Returns:
            `True` si el stock es mayor que cero.
        """
        return self.stock > 0

    def reduce_stock(self, quantity: int) -> None:
        """Disminuye el stock del producto si hay unidades suficientes.

        Args:
            quantity: Cantidad a reducir.

        Raises:
            ValueError: Si la cantidad es inválida o no hay stock suficiente.
        """
        if quantity <= 0:
            raise ValueError("La cantidad a reducir debe ser mayor que cero.")
        if quantity > self.stock:
            raise ValueError("No hay stock suficiente para realizar la operación.")
        self.stock -= quantity

    def increase_stock(self, quantity: int) -> None:
        """Aumenta el stock del producto.

        Args:
            quantity: Cantidad a aumentar.

        Raises:
            ValueError: Si la cantidad no es positiva.
        """
        if quantity <= 0:
            raise ValueError("La cantidad a aumentar debe ser mayor que cero.")
        self.stock += quantity


@dataclass
class ChatMessage:
    """Entidad de dominio que representa un mensaje de conversación."""

    session_id: str
    role: str
    message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    id: int | None = None

    def __post_init__(self) -> None:
        """Valida el contenido del mensaje de chat."""
        if not self.session_id or not self.session_id.strip():
            raise ValueError("El session_id no puede estar vacío.")
        if self.role not in {"user", "assistant"}:
            raise ValueError("El role debe ser 'user' o 'assistant'.")
        if not self.message or not self.message.strip():
            raise ValueError("El mensaje no puede estar vacío.")

    def is_user_message(self) -> bool:
        """Indica si el mensaje fue escrito por el usuario."""
        return self.role == "user"

    def is_assistant_message(self) -> bool:
        """Indica si el mensaje fue escrito por el asistente."""
        return self.role == "assistant"


@dataclass
class ChatContext:
    """Objeto de valor que modela el contexto reciente de una conversación."""

    messages: list[ChatMessage] = field(default_factory=list)

    def get_recent_messages(self, limit: int = 6) -> list[ChatMessage]:
        """Obtiene los últimos mensajes del historial.

        Args:
            limit: Número máximo de mensajes a devolver.

        Returns:
            Lista ordenada cronológicamente de mensajes recientes.
        """
        if limit <= 0:
            return []
        return self.messages[-limit:]

    def format_for_prompt(self, limit: int = 6) -> str:
        """Formatea el historial para incluirlo en el prompt del modelo.

        Args:
            limit: Número de mensajes recientes a incluir.

        Returns:
            Texto formateado con prefijos por rol.
        """
        recent: Sequence[ChatMessage] = self.get_recent_messages(limit=limit)
        if not recent:
            return "Sin historial previo."
        lines = [
            f"{'Usuario' if msg.role == 'user' else 'Asistente'}: {msg.message}"
            for msg in recent
        ]
        return "\n".join(lines)
