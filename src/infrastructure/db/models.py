"""Modelos ORM de SQLAlchemy para persistencia de datos.

Define la representación relacional de las entidades del dominio,
mapeando cada modelo a una tabla de la base de datos SQLite.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class ProductModel(Base):
    """Modelo ORM para la tabla ``products``.

    Representa un zapato en el catálogo del e-commerce. Incluye índices
    en las columnas ``brand`` y ``category`` para optimizar filtros frecuentes.

    Attributes:
        id (int): Clave primaria autoincremental.
        name (str): Nombre del producto (máx. 200 caracteres).
        brand (str): Marca del producto (máx. 100 caracteres).
        category (str): Categoría (Running, Casual, Formal) (máx. 100 caracteres).
        size (str): Talla del zapato (máx. 20 caracteres).
        color (str): Color del producto (máx. 50 caracteres).
        price (float): Precio en dólares.
        stock (int): Unidades disponibles en inventario.
        description (str): Descripción textual del producto.
    """

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[str] = mapped_column(String(20), nullable=False)
    color: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")

    __table_args__ = (
        Index("ix_products_brand", "brand"),
        Index("ix_products_category", "category"),
    )


class ChatMemoryModel(Base):
    """Modelo ORM para la tabla ``chat_memory``.

    Almacena cada mensaje de la conversación entre el usuario y el
    asistente de IA, agrupados por ``session_id``.

    Attributes:
        id (int): Clave primaria autoincremental.
        session_id (str): Identificador de la sesión de chat (indexado).
        role (str): Rol del autor (``'user'`` o ``'assistant'``).
        message (str): Contenido del mensaje.
        timestamp (datetime): Fecha y hora de creación del mensaje (UTC).
    """

    __tablename__ = "chat_memory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
