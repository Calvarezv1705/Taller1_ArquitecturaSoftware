"""Interfaces de repositorios del dominio.

Definen contratos de acceso a datos sin acoplarse a tecnología específica.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .entities import ChatMessage, Product


class IProductRepository(ABC):
    """Contrato para operaciones de persistencia de productos."""

    @abstractmethod
    def get_all(self) -> list[Product]:
        """Obtiene todos los productos registrados."""

    @abstractmethod
    def get_by_id(self, product_id: int) -> Product | None:
        """Obtiene un producto por su identificador."""

    @abstractmethod
    def get_by_brand(self, brand: str) -> list[Product]:
        """Obtiene productos por marca."""

    @abstractmethod
    def get_by_category(self, category: str) -> list[Product]:
        """Obtiene productos por categoría."""

    @abstractmethod
    def save(self, product: Product) -> Product:
        """Guarda o actualiza un producto."""

    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """Elimina un producto por su identificador."""


class IChatRepository(ABC):
    """Contrato para persistencia de mensajes de chat."""

    @abstractmethod
    def save_message(self, message: ChatMessage) -> ChatMessage:
        """Guarda un mensaje de una conversación."""

    @abstractmethod
    def get_session_history(self, session_id: str, limit: int = 10) -> list[ChatMessage]:
        """Obtiene el historial de una sesión en orden cronológico."""

    @abstractmethod
    def delete_session_history(self, session_id: str) -> int:
        """Elimina el historial completo de una sesión."""

    @abstractmethod
    def get_recent_messages(self, session_id: str, limit: int = 6) -> list[ChatMessage]:
        """Obtiene los últimos mensajes de una sesión para contexto."""
