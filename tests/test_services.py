"""Pruebas unitarias para servicios de aplicación."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from src.application.chat_service import ChatService
from src.application.dtos import ChatMessageRequestDTO, ProductDTO
from src.application.product_service import ProductService
from src.domain.entities import ChatMessage, Product
from src.domain.exceptions import ProductNotFoundError


@dataclass
class FakeProductRepository:
    """Repositorio en memoria para pruebas de productos."""

    products: list[Product]

    def get_all(self) -> list[Product]:
        return self.products

    def get_by_id(self, product_id: int) -> Product | None:
        return next((p for p in self.products if p.id == product_id), None)

    def get_by_brand(self, brand: str) -> list[Product]:
        return [p for p in self.products if p.brand.lower() == brand.lower()]

    def get_by_category(self, category: str) -> list[Product]:
        return [p for p in self.products if p.category.lower() == category.lower()]

    def save(self, product: Product) -> Product:
        if product.id is None:
            product.id = len(self.products) + 1
            self.products.append(product)
            return product
        for idx, existing in enumerate(self.products):
            if existing.id == product.id:
                self.products[idx] = product
                return product
        self.products.append(product)
        return product

    def delete(self, product_id: int) -> bool:
        before = len(self.products)
        self.products = [p for p in self.products if p.id != product_id]
        return len(self.products) < before


@dataclass
class FakeChatRepository:
    """Repositorio en memoria para pruebas de chat."""

    messages: list[ChatMessage]

    def save_message(self, message: ChatMessage) -> ChatMessage:
        self.messages.append(message)
        return message

    def get_session_history(self, session_id: str, limit: int = 10) -> list[ChatMessage]:
        result = [m for m in self.messages if m.session_id == session_id]
        return result[-limit:]

    def delete_session_history(self, session_id: str) -> int:
        before = len(self.messages)
        self.messages = [m for m in self.messages if m.session_id != session_id]
        return before - len(self.messages)

    def get_recent_messages(self, session_id: str, limit: int = 6) -> list[ChatMessage]:
        result = [m for m in self.messages if m.session_id == session_id]
        return result[-limit:]


class FakeAIService:
    """Proveedor de IA falso para pruebas deterministas."""

    async def generate_response(self, user_message: str, products: list, context) -> str:
        return f"Respuesta a: {user_message}"


class TestProductService:
    """Pruebas del servicio de productos."""

    def test_get_product_by_id_not_found(self) -> None:
        repo = FakeProductRepository(products=[])
        service = ProductService(repo)

        with pytest.raises(ProductNotFoundError):
            service.get_product_by_id(999)

    def test_create_product(self) -> None:
        repo = FakeProductRepository(products=[])
        service = ProductService(repo)

        dto = ProductDTO(
            name="Superstar",
            brand="Adidas",
            category="Casual",
            size="41",
            color="Blanco",
            price=100,
            stock=5,
            description="Clásico urbano",
        )

        created = service.create_product(dto)
        assert created.id is not None
        assert created.name == "Superstar"


class TestChatService:
    """Pruebas del servicio de chat."""

    @pytest.mark.asyncio
    async def test_process_message(self) -> None:
        product_repo = FakeProductRepository(
            products=[
                Product(
                    id=1,
                    name="Air Zoom",
                    brand="Nike",
                    category="Running",
                    size="42",
                    color="Negro",
                    price=120,
                    stock=3,
                )
            ]
        )
        chat_repo = FakeChatRepository(messages=[])
        service = ChatService(product_repo, chat_repo, FakeAIService())

        response = await service.process_message(
            ChatMessageRequestDTO(session_id="s1", message="Busco running")
        )

        assert response.session_id == "s1"
        assert "Respuesta a:" in response.assistant_message
        assert len(chat_repo.messages) == 2
