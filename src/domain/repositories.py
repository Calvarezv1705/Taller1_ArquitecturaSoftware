"""Interfaces de repositorios del dominio.

Definen contratos (clases abstractas) de acceso a datos sin acoplarse
a ninguna tecnología de persistencia específica. Las implementaciones
concretas residen en la capa de infraestructura.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .entities import ChatMessage, Product


class IProductRepository(ABC):
    """Contrato para operaciones de persistencia de productos.

    Las implementaciones concretas (por ejemplo ``SQLProductRepository``)
    deben heredar de esta clase e implementar todos los métodos abstractos.
    """

    @abstractmethod
    def get_all(self) -> list[Product]:
        """Obtiene todos los productos registrados en el catálogo.

        Returns:
            list[Product]: Lista de todas las entidades de producto.
        """

    @abstractmethod
    def get_by_id(self, product_id: int) -> Product | None:
        """Obtiene un producto por su identificador único.

        Args:
            product_id (int): Identificador del producto buscado.

        Returns:
            Product | None: La entidad del producto si existe, ``None`` en caso contrario.
        """

    @abstractmethod
    def get_by_brand(self, brand: str) -> list[Product]:
        """Obtiene todos los productos de una marca específica.

        Args:
            brand (str): Nombre de la marca a filtrar.

        Returns:
            list[Product]: Lista de productos que pertenecen a la marca indicada.
        """

    @abstractmethod
    def get_by_category(self, category: str) -> list[Product]:
        """Obtiene todos los productos de una categoría específica.

        Args:
            category (str): Nombre de la categoría a filtrar (Running, Casual, Formal).

        Returns:
            list[Product]: Lista de productos de la categoría indicada.
        """

    @abstractmethod
    def save(self, product: Product) -> Product:
        """Guarda o actualiza un producto en el repositorio.

        Si el producto tiene ``id``, se actualiza. Si no tiene ``id``,
        se crea como nuevo y se le asigna un identificador.

        Args:
            product (Product): Entidad del producto a persistir.

        Returns:
            Product: La entidad guardada con su ``id`` asignado.
        """

    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """Elimina un producto del repositorio por su identificador.

        Args:
            product_id (int): Identificador del producto a eliminar.

        Returns:
            bool: ``True`` si se eliminó correctamente, ``False`` si no existía.
        """


class IChatRepository(ABC):
    """Contrato para persistencia de mensajes de chat.

    Permite guardar, consultar y eliminar el historial de conversaciones
    por sesión de usuario.
    """

    @abstractmethod
    def save_message(self, message: ChatMessage) -> ChatMessage:
        """Guarda un mensaje de una conversación en el historial.

        Args:
            message (ChatMessage): Entidad del mensaje a persistir.

        Returns:
            ChatMessage: El mensaje guardado con su ``id`` asignado.
        """

    @abstractmethod
    def get_session_history(self, session_id: str, limit: int = 10) -> list[ChatMessage]:
        """Obtiene el historial completo de una sesión en orden cronológico.

        Args:
            session_id (str): Identificador de la sesión.
            limit (int): Número máximo de mensajes a retornar. Por defecto 10.

        Returns:
            list[ChatMessage]: Lista de mensajes ordenados del más antiguo al más reciente.
        """

    @abstractmethod
    def delete_session_history(self, session_id: str) -> int:
        """Elimina el historial completo de una sesión.

        Args:
            session_id (str): Identificador de la sesión a limpiar.

        Returns:
            int: Cantidad de mensajes eliminados.
        """

    @abstractmethod
    def get_recent_messages(self, session_id: str, limit: int = 6) -> list[ChatMessage]:
        """Obtiene los últimos mensajes de una sesión para contexto conversacional.

        Crucial para mantener la memoria de la conversación al interactuar
        con el servicio de IA.

        Args:
            session_id (str): Identificador de la sesión.
            limit (int): Número máximo de mensajes recientes. Por defecto 6.

        Returns:
            list[ChatMessage]: Lista de mensajes recientes en orden cronológico.
        """
