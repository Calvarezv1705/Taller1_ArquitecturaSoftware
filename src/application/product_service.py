"""Casos de uso para gestión de productos."""

from __future__ import annotations

from .dtos import ProductDTO
from ..domain.entities import Product
from ..domain.exceptions import ProductNotFoundError
from ..domain.repositories import IProductRepository


class ProductService:
    """Servicio de aplicación para operaciones de productos."""

    def __init__(self, product_repository: IProductRepository) -> None:
        """Inicializa el servicio con el repositorio de productos."""
        self.product_repository = product_repository

    def get_all_products(self) -> list[ProductDTO]:
        """Obtiene todos los productos del catálogo."""
        products = self.product_repository.get_all()
        return [ProductDTO.model_validate(product) for product in products]

    def get_product_by_id(self, product_id: int) -> ProductDTO:
        """Obtiene un producto por ID y falla si no existe."""
        product = self.product_repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(product_id=product_id)
        return ProductDTO.model_validate(product)

    def search_products(self, brand: str | None = None, category: str | None = None) -> list[ProductDTO]:
        """Busca productos por filtros simples de marca y categoría."""
        if brand and category:
            products = [
                p
                for p in self.product_repository.get_by_brand(brand)
                if p.category.lower() == category.lower()
            ]
        elif brand:
            products = self.product_repository.get_by_brand(brand)
        elif category:
            products = self.product_repository.get_by_category(category)
        else:
            products = self.product_repository.get_all()
        return [ProductDTO.model_validate(product) for product in products]

    def create_product(self, product_dto: ProductDTO) -> ProductDTO:
        """Crea un producto nuevo en el catálogo."""
        product = Product(**product_dto.model_dump(exclude={"id"}))
        saved = self.product_repository.save(product)
        return ProductDTO.model_validate(saved)

    def update_product(self, product_id: int, product_dto: ProductDTO) -> ProductDTO:
        """Actualiza un producto existente por ID."""
        existing = self.product_repository.get_by_id(product_id)
        if existing is None:
            raise ProductNotFoundError(product_id=product_id)

        updated = Product(
            id=product_id,
            **product_dto.model_dump(exclude={"id"}),
        )
        saved = self.product_repository.save(updated)
        return ProductDTO.model_validate(saved)

    def delete_product(self, product_id: int) -> bool:
        """Elimina un producto. Lanza error si no existe."""
        existing = self.product_repository.get_by_id(product_id)
        if existing is None:
            raise ProductNotFoundError(product_id=product_id)
        return self.product_repository.delete(product_id)

    def get_available_products(self) -> list[ProductDTO]:
        """Retorna solo productos con stock mayor que cero."""
        products = self.product_repository.get_all()
        available = [product for product in products if product.is_available()]
        return [ProductDTO.model_validate(product) for product in available]
