"""Entidades y objetos de valor del dominio.

Este módulo contiene el núcleo de reglas de negocio para productos y chat.
Las entidades aquí definidas no dependen de frameworks, bases de datos ni
servicios externos, respetando el principio de independencia del dominio.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Sequence


@dataclass
class Product:
    """Entidad de dominio que representa un producto (zapato) del e-commerce.

    Contiene la lógica de negocio relacionada con productos, incluyendo
    validaciones de precio, stock y disponibilidad.

    Attributes:
        name (str): Nombre del producto. No puede estar vacío.
        brand (str): Marca del producto (Nike, Adidas, Puma, etc.).
        category (str): Categoría del producto (Running, Casual, Formal).
        size (str): Talla del zapato.
        color (str): Color del producto.
        price (float): Precio en dólares. Debe ser mayor que cero.
        stock (int): Cantidad disponible en inventario. No puede ser negativo.
        description (str): Descripción opcional del producto.
        id (int | None): Identificador único. ``None`` si aún no fue persistido.

    Example:
        >>> producto = Product(
        ...     name="Air Max", brand="Nike", category="Running",
        ...     size="42", color="Negro", price=120.0, stock=5,
        ... )
        >>> producto.is_available()
        True
    """

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
        """Valida las reglas de negocio al crear la entidad.

        Raises:
            ValueError: Si el nombre está vacío, el precio no es positivo
                o el stock es negativo.
        """
        if not self.name or not self.name.strip():
            raise ValueError("El nombre del producto no puede estar vacío.")
        if self.price <= 0:
            raise ValueError("El precio debe ser mayor que cero.")
        if self.stock < 0:
            raise ValueError("El stock no puede ser negativo.")

    def is_available(self) -> bool:
        """Indica si el producto está disponible para la venta.

        Returns:
            bool: ``True`` si el stock es mayor que cero.

        Example:
            >>> producto = Product(name="X", brand="B", category="C",
            ...     size="40", color="Rojo", price=50.0, stock=0)
            >>> producto.is_available()
            False
        """
        return self.stock > 0

    def reduce_stock(self, quantity: int) -> None:
        """Disminuye el stock del producto si hay unidades suficientes.

        Se usa típicamente cuando se realiza una venta.

        Args:
            quantity (int): Cantidad a reducir. Debe ser positiva.

        Raises:
            ValueError: Si la cantidad es menor o igual a cero, o si no
                hay stock suficiente para cubrir la reducción.

        Example:
            >>> producto = Product(name="Air Max", brand="Nike",
            ...     category="Running", size="42", color="Negro",
            ...     price=120.0, stock=10)
            >>> producto.reduce_stock(3)
            >>> producto.stock
            7
        """
        if quantity <= 0:
            raise ValueError("La cantidad a reducir debe ser mayor que cero.")
        if quantity > self.stock:
            raise ValueError("No hay stock suficiente para realizar la operación.")
        self.stock -= quantity

    def increase_stock(self, quantity: int) -> None:
        """Aumenta el stock del producto.

        Se usa al recibir reabastecimiento de inventario.

        Args:
            quantity (int): Cantidad a aumentar. Debe ser positiva.

        Raises:
            ValueError: Si la cantidad no es positiva.

        Example:
            >>> producto = Product(name="Air Max", brand="Nike",
            ...     category="Running", size="42", color="Negro",
            ...     price=120.0, stock=5)
            >>> producto.increase_stock(10)
            >>> producto.stock
            15
        """
        if quantity <= 0:
            raise ValueError("La cantidad a aumentar debe ser mayor que cero.")
        self.stock += quantity


@dataclass
class ChatMessage:
    """Entidad de dominio que representa un mensaje en la conversación.

    Cada mensaje pertenece a una sesión y fue escrito por el usuario
    o por el asistente de IA.

    Attributes:
        session_id (str): Identificador único de la sesión de chat.
        role (str): Rol del autor; debe ser ``'user'`` o ``'assistant'``.
        message (str): Contenido del mensaje.
        timestamp (datetime): Fecha y hora de creación del mensaje (UTC).
        id (int | None): Identificador único. ``None`` si no fue persistido.

    Example:
        >>> msg = ChatMessage(session_id="s1", role="user", message="Hola")
        >>> msg.is_user_message()
        True
    """

    session_id: str
    role: str
    message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    id: int | None = None

    def __post_init__(self) -> None:
        """Valida el contenido del mensaje de chat.

        Raises:
            ValueError: Si ``session_id`` o ``message`` están vacíos, o si
                ``role`` no es ``'user'`` ni ``'assistant'``.
        """
        if not self.session_id or not self.session_id.strip():
            raise ValueError("El session_id no puede estar vacío.")
        if self.role not in {"user", "assistant"}:
            raise ValueError("El role debe ser 'user' o 'assistant'.")
        if not self.message or not self.message.strip():
            raise ValueError("El mensaje no puede estar vacío.")

    def is_user_message(self) -> bool:
        """Indica si el mensaje fue escrito por el usuario.

        Returns:
            bool: ``True`` si ``role == 'user'``.
        """
        return self.role == "user"

    def is_assistant_message(self) -> bool:
        """Indica si el mensaje fue escrito por el asistente.

        Returns:
            bool: ``True`` si ``role == 'assistant'``.
        """
        return self.role == "assistant"


@dataclass
class ChatContext:
    """Objeto de valor que modela el contexto reciente de una conversación.

    Mantiene los mensajes recientes para que la IA tenga memoria de la
    conversación y pueda dar respuestas coherentes.

    Attributes:
        messages (list[ChatMessage]): Lista completa de mensajes de la sesión.

    Example:
        >>> contexto = ChatContext(messages=[])
        >>> contexto.format_for_prompt()
        'Sin historial previo.'
    """

    messages: list[ChatMessage] = field(default_factory=list)

    def get_recent_messages(self, limit: int = 6) -> list[ChatMessage]:
        """Obtiene los últimos mensajes del historial.

        Args:
            limit (int): Número máximo de mensajes a devolver. Por defecto 6.

        Returns:
            list[ChatMessage]: Lista ordenada cronológicamente de los
                mensajes más recientes, limitada a ``limit`` elementos.
        """
        if limit <= 0:
            return []
        return self.messages[-limit:]

    def format_for_prompt(self, limit: int = 6) -> str:
        """Formatea el historial para incluirlo en el prompt del modelo de IA.

        Cada mensaje se prefija con ``'Usuario:'`` o ``'Asistente:'`` según
        el rol, y se concatenan con saltos de línea.

        Args:
            limit (int): Número de mensajes recientes a incluir. Por defecto 6.

        Returns:
            str: Texto formateado con el historial conversacional, o
                ``'Sin historial previo.'`` si no hay mensajes.

        Example:
            >>> msgs = [
            ...     ChatMessage(session_id="s1", role="user", message="Hola"),
            ...     ChatMessage(session_id="s1", role="assistant", message="¡Hola!"),
            ... ]
            >>> ChatContext(messages=msgs).format_for_prompt()
            'Usuario: Hola\\nAsistente: ¡Hola!'
        """
        recent: Sequence[ChatMessage] = self.get_recent_messages(limit=limit)
        if not recent:
            return "Sin historial previo."
        lines = [
            f"{'Usuario' if msg.role == 'user' else 'Asistente'}: {msg.message}"
            for msg in recent
        ]
        return "\n".join(lines)
