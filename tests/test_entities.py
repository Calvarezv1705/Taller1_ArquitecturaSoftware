"""Pruebas unitarias para entidades del dominio.

Cubren validaciones de creación, métodos de negocio y casos extremos
de Product, ChatMessage y ChatContext.
"""

from datetime import UTC, datetime

import pytest

from src.domain.entities import ChatContext, ChatMessage, Product


# ---------------------------------------------------------------------------
# Product
# ---------------------------------------------------------------------------


class TestProduct:
    """Pruebas de validaciones y comportamiento de ``Product``."""

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
        with pytest.raises(ValueError, match="precio"):
            Product(
                name="Air Max", brand="Nike", category="Running",
                size="42", color="Negro", price=0, stock=5,
            )

    def test_product_negative_price_raises_error(self) -> None:
        """Debe fallar si el precio es negativo."""
        with pytest.raises(ValueError, match="precio"):
            Product(
                name="Air Max", brand="Nike", category="Running",
                size="42", color="Negro", price=-10.0, stock=5,
            )

    def test_product_invalid_name_raises_error(self) -> None:
        """Debe fallar si el nombre está vacío."""
        with pytest.raises(ValueError, match="nombre"):
            Product(
                name="", brand="Nike", category="Running",
                size="42", color="Negro", price=100.0, stock=5,
            )

    def test_product_whitespace_name_raises_error(self) -> None:
        """Debe fallar si el nombre es solo espacios en blanco."""
        with pytest.raises(ValueError, match="nombre"):
            Product(
                name="   ", brand="Nike", category="Running",
                size="42", color="Negro", price=100.0, stock=5,
            )

    def test_product_negative_stock_raises_error(self) -> None:
        """Debe fallar si el stock es negativo."""
        with pytest.raises(ValueError, match="stock"):
            Product(
                name="Air Max", brand="Nike", category="Running",
                size="42", color="Negro", price=100.0, stock=-1,
            )

    def test_product_zero_stock_is_valid(self) -> None:
        """Un producto con stock cero debe crearse correctamente."""
        product = Product(
            name="Air Max", brand="Nike", category="Running",
            size="42", color="Negro", price=100.0, stock=0,
        )
        assert product.stock == 0

    def test_product_not_available_when_zero_stock(self) -> None:
        """Un producto con stock cero no debe estar disponible."""
        product = Product(
            name="Air Max", brand="Nike", category="Running",
            size="42", color="Negro", price=100.0, stock=0,
        )
        assert product.is_available() is False

    def test_reduce_stock(self) -> None:
        """Debe disminuir el stock cuando la cantidad es válida."""
        product = Product(
            name="Air Max", brand="Nike", category="Running",
            size="42", color="Negro", price=120.0, stock=5,
        )
        product.reduce_stock(2)
        assert product.stock == 3

    def test_reduce_stock_to_zero(self) -> None:
        """Debe permitir reducir el stock exactamente a cero."""
        product = Product(
            name="Air Max", brand="Nike", category="Running",
            size="42", color="Negro", price=120.0, stock=3,
        )
        product.reduce_stock(3)
        assert product.stock == 0
        assert product.is_available() is False

    def test_reduce_stock_insufficient_raises_error(self) -> None:
        """Debe fallar si se intenta reducir más stock del disponible."""
        product = Product(
            name="Air Max", brand="Nike", category="Running",
            size="42", color="Negro", price=120.0, stock=1,
        )
        with pytest.raises(ValueError, match="stock suficiente"):
            product.reduce_stock(2)

    def test_reduce_stock_zero_raises_error(self) -> None:
        """Debe fallar si se intenta reducir con cantidad cero."""
        product = Product(
            name="Air Max", brand="Nike", category="Running",
            size="42", color="Negro", price=120.0, stock=5,
        )
        with pytest.raises(ValueError, match="mayor que cero"):
            product.reduce_stock(0)

    def test_reduce_stock_negative_raises_error(self) -> None:
        """Debe fallar si se intenta reducir con cantidad negativa."""
        product = Product(
            name="Air Max", brand="Nike", category="Running",
            size="42", color="Negro", price=120.0, stock=5,
        )
        with pytest.raises(ValueError, match="mayor que cero"):
            product.reduce_stock(-1)

    def test_increase_stock(self) -> None:
        """Debe aumentar el stock cuando la cantidad es válida."""
        product = Product(
            name="Air Max", brand="Nike", category="Running",
            size="42", color="Negro", price=120.0, stock=5,
        )
        product.increase_stock(10)
        assert product.stock == 15

    def test_increase_stock_zero_raises_error(self) -> None:
        """Debe fallar si se intenta aumentar con cantidad cero."""
        product = Product(
            name="Air Max", brand="Nike", category="Running",
            size="42", color="Negro", price=120.0, stock=5,
        )
        with pytest.raises(ValueError, match="mayor que cero"):
            product.increase_stock(0)

    def test_increase_stock_negative_raises_error(self) -> None:
        """Debe fallar si se intenta aumentar con cantidad negativa."""
        product = Product(
            name="Air Max", brand="Nike", category="Running",
            size="42", color="Negro", price=120.0, stock=5,
        )
        with pytest.raises(ValueError, match="mayor que cero"):
            product.increase_stock(-3)


# ---------------------------------------------------------------------------
# ChatMessage
# ---------------------------------------------------------------------------


class TestChatMessage:
    """Pruebas para validación de ``ChatMessage``."""

    def test_chat_message_valid_user(self) -> None:
        """Debe crear un mensaje de usuario válido."""
        msg = ChatMessage(
            session_id="user-1",
            role="user",
            message="Hola",
            timestamp=datetime.now(UTC),
        )
        assert msg.is_user_message() is True
        assert msg.is_assistant_message() is False

    def test_chat_message_valid_assistant(self) -> None:
        """Debe crear un mensaje de asistente válido."""
        msg = ChatMessage(
            session_id="user-1",
            role="assistant",
            message="¡Hola!",
        )
        assert msg.is_assistant_message() is True
        assert msg.is_user_message() is False

    def test_chat_message_invalid_role(self) -> None:
        """Debe fallar con rol no permitido."""
        with pytest.raises(ValueError, match="role"):
            ChatMessage(session_id="user-1", role="system", message="Hola")

    def test_chat_message_empty_message_raises_error(self) -> None:
        """Debe fallar si el mensaje está vacío."""
        with pytest.raises(ValueError, match="mensaje"):
            ChatMessage(session_id="user-1", role="user", message="")

    def test_chat_message_whitespace_message_raises_error(self) -> None:
        """Debe fallar si el mensaje es solo espacios."""
        with pytest.raises(ValueError, match="mensaje"):
            ChatMessage(session_id="user-1", role="user", message="   ")

    def test_chat_message_empty_session_id_raises_error(self) -> None:
        """Debe fallar si session_id está vacío."""
        with pytest.raises(ValueError, match="session_id"):
            ChatMessage(session_id="", role="user", message="Hola")

    def test_chat_message_whitespace_session_id_raises_error(self) -> None:
        """Debe fallar si session_id es solo espacios."""
        with pytest.raises(ValueError, match="session_id"):
            ChatMessage(session_id="   ", role="user", message="Hola")

    def test_chat_message_default_timestamp(self) -> None:
        """El timestamp debe asignarse automáticamente si no se proporciona."""
        msg = ChatMessage(session_id="s1", role="user", message="Hola")
        assert msg.timestamp is not None


# ---------------------------------------------------------------------------
# ChatContext
# ---------------------------------------------------------------------------


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

    def test_format_for_prompt_empty(self) -> None:
        """Debe retornar texto de historial vacío cuando no hay mensajes."""
        context = ChatContext(messages=[])
        assert context.format_for_prompt() == "Sin historial previo."

    def test_get_recent_messages_limit(self) -> None:
        """Debe respetar el límite de mensajes recientes."""
        messages = [
            ChatMessage(session_id="s1", role="user", message=f"Msg {i}")
            for i in range(10)
        ]
        context = ChatContext(messages=messages)
        recent = context.get_recent_messages(limit=3)
        assert len(recent) == 3
        assert recent[0].message == "Msg 7"

    def test_get_recent_messages_less_than_limit(self) -> None:
        """Si hay menos mensajes que el límite, retorna todos."""
        messages = [
            ChatMessage(session_id="s1", role="user", message="Único"),
        ]
        context = ChatContext(messages=messages)
        recent = context.get_recent_messages(limit=6)
        assert len(recent) == 1

    def test_get_recent_messages_zero_limit(self) -> None:
        """Con límite cero debe retornar lista vacía."""
        messages = [
            ChatMessage(session_id="s1", role="user", message="Hola"),
        ]
        context = ChatContext(messages=messages)
        assert context.get_recent_messages(limit=0) == []
