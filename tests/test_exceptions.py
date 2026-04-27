"""Pruebas unitarias para excepciones del dominio."""

from src.domain.exceptions import ChatServiceError, InvalidProductDataError, ProductNotFoundError


class TestProductNotFoundError:
    """Pruebas de ProductNotFoundError."""

    def test_default_message(self):
        """Debe usar mensaje por defecto sin product_id."""
        exc = ProductNotFoundError()
        assert "no se encontró" in str(exc).lower()

    def test_with_product_id(self):
        """Debe incluir el ID en el mensaje."""
        exc = ProductNotFoundError(product_id=42)
        assert "42" in str(exc)

    def test_custom_message(self):
        """Debe aceptar mensaje personalizado."""
        exc = ProductNotFoundError(message="Personalizado")
        assert str(exc) == "Personalizado"


class TestInvalidProductDataError:
    """Pruebas de InvalidProductDataError."""

    def test_default_message(self):
        """Debe usar mensaje por defecto."""
        exc = InvalidProductDataError()
        assert "no son válidos" in str(exc).lower()

    def test_custom_message(self):
        """Debe aceptar mensaje personalizado."""
        exc = InvalidProductDataError("Precio inválido")
        assert str(exc) == "Precio inválido"


class TestChatServiceError:
    """Pruebas de ChatServiceError."""

    def test_default_message(self):
        """Debe usar mensaje por defecto."""
        exc = ChatServiceError()
        assert "error" in str(exc).lower()

    def test_custom_message(self):
        """Debe aceptar mensaje personalizado."""
        exc = ChatServiceError("Gemini no disponible")
        assert str(exc) == "Gemini no disponible"
