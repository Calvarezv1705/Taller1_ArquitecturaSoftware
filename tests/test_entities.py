"""Pruebas unitarias para entidades del dominio."""

from datetime import UTC, datetime

import pytest

from src.domain.entities import ChatContext, ChatMessage, Product


class TestProduct:
    """Pruebas de validaciones y comportamiento de `Product`."""

    def test_product_valid_creation(self) -> None:
        """Debe crear un producto válido correctamente."""
        product = Product(
            name="Air Max",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=120.0,
            stock=5,
        )
        assert product.name == "Air Max"
        assert product.is_available() is True

    def test_product_invalid_price_raises_error(self) -> None:
        """Debe fallar si el precio es menor o igual que cero."""
        with pytest.raises(ValueError):
            Product(
                name="Air Max",
                brand="Nike",
                category="Running",
                size="42",
                color="Negro",
                price=0,
                stock=5,
            )

    def test_reduce_stock(self) -> None:
        """Debe disminuir el stock cuando la cantidad es válida."""
        product = Product(
            name="Air Max",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=120.0,
            stock=5,
        )
        product.reduce_stock(2)
        assert product.stock == 3

    def test_reduce_stock_insufficient_raises_error(self) -> None:
        """Debe fallar si se intenta reducir más stock del disponible."""
        product = Product(
            name="Air Max",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=120.0,
            stock=1,
        )
        with pytest.raises(ValueError):
            product.reduce_stock(2)


class TestChatMessage:
    """Pruebas para validación de `ChatMessage`."""

    def test_chat_message_valid(self) -> None:
        """Debe crear un mensaje de usuario válido."""
        msg = ChatMessage(
            session_id="user-1",
            role="user",
            message="Hola",
            timestamp=datetime.now(UTC),
        )
        assert msg.is_user_message() is True
        assert msg.is_assistant_message() is False

    def test_chat_message_invalid_role(self) -> None:
        """Debe fallar con rol no permitido."""
        with pytest.raises(ValueError):
            ChatMessage(session_id="user-1", role="system", message="Hola")


class TestChatContext:
    """Pruebas para formato de contexto conversacional."""

    def test_format_for_prompt(self) -> None:
        """Debe formar un historial legible para el prompt."""
        messages = [
            ChatMessage(session_id="s1", role="user", message="Hola"),
            ChatMessage(session_id="s1", role="assistant", message="¡Hola!"),
        ]
        context = ChatContext(messages=messages)
        formatted = context.format_for_prompt()

        assert "Usuario: Hola" in formatted
        assert "Asistente: ¡Hola!" in formatted
