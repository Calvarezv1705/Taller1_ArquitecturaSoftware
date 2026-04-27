"""Pruebas unitarias para DTOs con validación Pydantic."""

import pytest
from pydantic import ValidationError
from src.application.dtos import ChatMessageRequestDTO, ProductDTO


class TestProductDTO:
    """Pruebas de validación de ProductDTO."""

    def test_valid_product_dto(self):
        """Debe crear un DTO válido."""
        dto = ProductDTO(name="Air Max", brand="Nike", category="Running", size="42", color="Negro", price=120.0, stock=5)
        assert dto.name == "Air Max"

    def test_price_zero_raises(self):
        """Precio cero debe fallar."""
        with pytest.raises(ValidationError):
            ProductDTO(name="X", brand="N", category="R", size="42", color="N", price=0, stock=5)

    def test_price_negative_raises(self):
        """Precio negativo debe fallar."""
        with pytest.raises(ValidationError):
            ProductDTO(name="X", brand="N", category="R", size="42", color="N", price=-10, stock=5)

    def test_stock_negative_raises(self):
        """Stock negativo debe fallar."""
        with pytest.raises(ValidationError):
            ProductDTO(name="X", brand="N", category="R", size="42", color="N", price=100, stock=-1)

    def test_empty_name_raises(self):
        """Nombre vacío debe fallar."""
        with pytest.raises(ValidationError):
            ProductDTO(name="", brand="N", category="R", size="42", color="N", price=100, stock=5)

    def test_whitespace_name_raises(self):
        """Nombre con solo espacios debe fallar."""
        with pytest.raises(ValidationError):
            ProductDTO(name="   ", brand="N", category="R", size="42", color="N", price=100, stock=5)


class TestChatMessageRequestDTO:
    """Pruebas de validación de ChatMessageRequestDTO."""

    def test_valid_request(self):
        """Debe crear un request válido."""
        dto = ChatMessageRequestDTO(session_id="user1", message="Hola")
        assert dto.session_id == "user1"

    def test_empty_message_raises(self):
        """Mensaje vacío debe fallar."""
        with pytest.raises(ValidationError):
            ChatMessageRequestDTO(session_id="user1", message="")

    def test_empty_session_id_raises(self):
        """Session ID vacío debe fallar."""
        with pytest.raises(ValidationError):
            ChatMessageRequestDTO(session_id="", message="Hola")

    def test_whitespace_message_raises(self):
        """Mensaje con solo espacios debe fallar."""
        with pytest.raises(ValidationError):
            ChatMessageRequestDTO(session_id="user1", message="   ")
