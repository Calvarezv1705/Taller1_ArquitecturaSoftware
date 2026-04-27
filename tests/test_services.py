"""Pruebas unitarias para servicios de aplicación."""

from __future__ import annotations
from dataclasses import dataclass
import pytest
from src.application.chat_service import ChatService
from src.application.dtos import ChatMessageRequestDTO, ProductDTO
from src.application.product_service import ProductService
from src.domain.entities import ChatMessage, Product
from src.domain.exceptions import ChatServiceError, ProductNotFoundError

@dataclass
class FakeProductRepository:
    """Repositorio en memoria para pruebas."""
    products: list[Product]
    def get_all(self): return self.products
    def get_by_id(self, pid): return next((p for p in self.products if p.id == pid), None)
    def get_by_brand(self, b): return [p for p in self.products if p.brand.lower() == b.lower()]
    def get_by_category(self, c): return [p for p in self.products if p.category.lower() == c.lower()]
    def save(self, p):
        if p.id is None:
            p.id = len(self.products) + 1
            self.products.append(p)
            return p
        for i, e in enumerate(self.products):
            if e.id == p.id: self.products[i] = p; return p
        self.products.append(p); return p
    def delete(self, pid):
        b = len(self.products); self.products = [p for p in self.products if p.id != pid]; return len(self.products) < b

@dataclass
class FakeChatRepository:
    """Repositorio en memoria para pruebas de chat."""
    messages: list[ChatMessage]
    def save_message(self, message): self.messages.append(message); return message
    def get_session_history(self, session_id, limit=10): return [m for m in self.messages if m.session_id == session_id][-limit:]
    def delete_session_history(self, session_id):
        b = len(self.messages); self.messages = [m for m in self.messages if m.session_id != session_id]; return b - len(self.messages)
    def get_recent_messages(self, session_id, limit=6): return [m for m in self.messages if m.session_id == session_id][-limit:]

class FakeAIService:
    """IA falsa determinista."""
    async def generate_response(self, user_message, products, context): return f"Respuesta a: {user_message}"

class FailingAIService:
    """IA que siempre falla."""
    async def generate_response(self, user_message, products, context): raise RuntimeError("Error simulado")

def _p(pid=1, **kw):
    d = dict(id=pid, name="Air Zoom", brand="Nike", category="Running", size="42", color="Negro", price=120.0, stock=3)
    d.update(kw); return Product(**d)

class TestProductService:
    """Pruebas del servicio de productos."""
    def test_get_all(self):
        s = ProductService(FakeProductRepository([_p(1), _p(2, name="X")])); assert len(s.get_all_products()) == 2
    def test_get_by_id(self):
        s = ProductService(FakeProductRepository([_p(1)])); assert s.get_product_by_id(1).name == "Air Zoom"
    def test_get_by_id_not_found(self):
        with pytest.raises(ProductNotFoundError): ProductService(FakeProductRepository([])).get_product_by_id(999)
    def test_create(self):
        s = ProductService(FakeProductRepository([]))
        c = s.create_product(ProductDTO(name="S", brand="A", category="C", size="41", color="B", price=100, stock=5))
        assert c.id is not None
    def test_update(self):
        s = ProductService(FakeProductRepository([_p(1)]))
        u = s.update_product(1, ProductDTO(name="V2", brand="N", category="R", size="42", color="B", price=130, stock=10))
        assert u.name == "V2"
    def test_update_not_found(self):
        with pytest.raises(ProductNotFoundError):
            ProductService(FakeProductRepository([])).update_product(9, ProductDTO(name="X", brand="N", category="R", size="42", color="N", price=100, stock=5))
    def test_delete(self):
        r = FakeProductRepository([_p(1)]); assert ProductService(r).delete_product(1) is True; assert len(r.products) == 0
    def test_delete_not_found(self):
        with pytest.raises(ProductNotFoundError): ProductService(FakeProductRepository([])).delete_product(9)
    def test_available(self):
        s = ProductService(FakeProductRepository([_p(1, stock=5), _p(2, name="X", stock=0)]))
        assert len(s.get_available_products()) == 1
    def test_search_brand(self):
        s = ProductService(FakeProductRepository([_p(1, brand="Nike"), _p(2, name="U", brand="Adidas")]))
        assert len(s.search_products(brand="Nike")) == 1
    def test_search_category(self):
        s = ProductService(FakeProductRepository([_p(1, category="Running"), _p(2, name="O", category="Formal")]))
        assert len(s.search_products(category="Formal")) == 1
    def test_search_both(self):
        s = ProductService(FakeProductRepository([_p(1, brand="Nike", category="Running"), _p(2, name="SB", brand="Nike", category="Casual")]))
        assert len(s.search_products(brand="Nike", category="Running")) == 1
    def test_search_none(self):
        s = ProductService(FakeProductRepository([_p(1), _p(2, name="X")])); assert len(s.search_products()) == 2

class TestChatService:
    """Pruebas del servicio de chat."""
    @pytest.mark.asyncio
    async def test_process(self):
        s = ChatService(FakeProductRepository([_p(1)]), FakeChatRepository([]), FakeAIService())
        r = await s.process_message(ChatMessageRequestDTO(session_id="s1", message="Busco running"))
        assert r.session_id == "s1" and "Respuesta a:" in r.assistant_message
    @pytest.mark.asyncio
    async def test_saves_both(self):
        cr = FakeChatRepository([]); s = ChatService(FakeProductRepository([]), cr, FakeAIService())
        await s.process_message(ChatMessageRequestDTO(session_id="s1", message="Hola"))
        assert cr.messages[0].role == "user" and cr.messages[1].role == "assistant"
    @pytest.mark.asyncio
    async def test_no_ai(self):
        with pytest.raises(ChatServiceError):
            await ChatService(FakeProductRepository([]), FakeChatRepository([]), None).process_message(ChatMessageRequestDTO(session_id="s1", message="H"))
    @pytest.mark.asyncio
    async def test_ai_fail(self):
        with pytest.raises(ChatServiceError):
            await ChatService(FakeProductRepository([]), FakeChatRepository([]), FailingAIService()).process_message(ChatMessageRequestDTO(session_id="s1", message="H"))
    def test_history(self):
        ms = [ChatMessage(session_id="s1", role="user", message="H"), ChatMessage(session_id="s1", role="assistant", message="R")]
        h = ChatService(FakeProductRepository([]), FakeChatRepository(ms)).get_session_history("s1")
        assert len(h) == 2
    def test_clear(self):
        ms = [ChatMessage(session_id="s1", role="user", message="H")]
        assert ChatService(FakeProductRepository([]), FakeChatRepository(ms)).clear_session_history("s1") == 1
