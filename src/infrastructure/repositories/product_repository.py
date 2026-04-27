"""Repositorio SQLAlchemy para productos."""

from __future__ import annotations

from sqlalchemy.orm import Session

from src.domain.entities import Product
from src.domain.repositories import IProductRepository
from src.infrastructure.db.models import ProductModel


class SQLProductRepository(IProductRepository):
    """Implementación concreta de `IProductRepository` usando SQLAlchemy."""

    def __init__(self, db: Session) -> None:
        """Inicializa el repositorio con sesión de base de datos."""
        self.db = db

    def get_all(self) -> list[Product]:
        """Obtiene todos los productos."""
        models = self.db.query(ProductModel).all()
        return [self._model_to_entity(model) for model in models]

    def get_by_id(self, product_id: int) -> Product | None:
        """Obtiene un producto por ID."""
        model = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        return self._model_to_entity(model) if model else None

    def get_by_brand(self, brand: str) -> list[Product]:
        """Obtiene productos por marca (case-insensitive)."""
        models = self.db.query(ProductModel).filter(ProductModel.brand.ilike(brand)).all()
        return [self._model_to_entity(model) for model in models]

    def get_by_category(self, category: str) -> list[Product]:
        """Obtiene productos por categoría (case-insensitive)."""
        models = self.db.query(ProductModel).filter(ProductModel.category.ilike(category)).all()
        return [self._model_to_entity(model) for model in models]

    def save(self, product: Product) -> Product:
        """Guarda un producto nuevo o actualiza uno existente."""
        if product.id is None:
            model = self._entity_to_model(product)
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            return self._model_to_entity(model)

        existing = self.db.query(ProductModel).filter(ProductModel.id == product.id).first()
        if existing is None:
            model = self._entity_to_model(product)
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            return self._model_to_entity(model)

        existing.name = product.name
        existing.brand = product.brand
        existing.category = product.category
        existing.size = product.size
        existing.color = product.color
        existing.price = product.price
        existing.stock = product.stock
        existing.description = product.description
        self.db.commit()
        self.db.refresh(existing)
        return self._model_to_entity(existing)

    def delete(self, product_id: int) -> bool:
        """Elimina un producto por ID."""
        model = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not model:
            return False
        self.db.delete(model)
        self.db.commit()
        return True

    @staticmethod
    def _model_to_entity(model: ProductModel) -> Product:
        """Convierte un modelo ORM en entidad de dominio."""
        return Product(
            id=model.id,
            name=model.name,
            brand=model.brand,
            category=model.category,
            size=model.size,
            color=model.color,
            price=model.price,
            stock=model.stock,
            description=model.description,
        )

    @staticmethod
    def _entity_to_model(entity: Product) -> ProductModel:
        """Convierte una entidad de dominio en modelo ORM."""
        return ProductModel(
            id=entity.id,
            name=entity.name,
            brand=entity.brand,
            category=entity.category,
            size=entity.size,
            color=entity.color,
            price=entity.price,
            stock=entity.stock,
            description=entity.description,
        )
