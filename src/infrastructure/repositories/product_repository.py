"""Repositorio SQLAlchemy para productos.

Implementa el contrato ``IProductRepository`` del dominio utilizando
SQLAlchemy como ORM y SQLite como motor de base de datos.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from src.domain.entities import Product
from src.domain.repositories import IProductRepository
from src.infrastructure.db.models import ProductModel


class SQLProductRepository(IProductRepository):
    """Implementación concreta de ``IProductRepository`` usando SQLAlchemy.

    Traduce las operaciones de dominio en consultas SQL a través del ORM,
    convirtiendo entre modelos ORM y entidades de dominio.

    Attributes:
        db (Session): Sesión activa de SQLAlchemy inyectada en el constructor.
    """

    def __init__(self, db: Session) -> None:
        """Inicializa el repositorio con una sesión de base de datos.

        Args:
            db (Session): Sesión activa de SQLAlchemy.
        """
        self.db = db

    def get_all(self) -> list[Product]:
        """Obtiene todos los productos del catálogo.

        Returns:
            list[Product]: Lista de entidades de producto.
        """
        models = self.db.query(ProductModel).all()
        return [self._model_to_entity(model) for model in models]

    def get_by_id(self, product_id: int) -> Product | None:
        """Obtiene un producto por su identificador único.

        Args:
            product_id (int): Identificador del producto buscado.

        Returns:
            Product | None: La entidad del producto si existe, ``None`` en caso contrario.
        """
        model = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        return self._model_to_entity(model) if model else None

    def get_by_brand(self, brand: str) -> list[Product]:
        """Obtiene productos por marca (búsqueda insensible a mayúsculas).

        Args:
            brand (str): Nombre de la marca a filtrar.

        Returns:
            list[Product]: Lista de productos de la marca indicada.
        """
        models = self.db.query(ProductModel).filter(ProductModel.brand.ilike(brand)).all()
        return [self._model_to_entity(model) for model in models]

    def get_by_category(self, category: str) -> list[Product]:
        """Obtiene productos por categoría (búsqueda insensible a mayúsculas).

        Args:
            category (str): Nombre de la categoría a filtrar.

        Returns:
            list[Product]: Lista de productos de la categoría indicada.
        """
        models = self.db.query(ProductModel).filter(ProductModel.category.ilike(category)).all()
        return [self._model_to_entity(model) for model in models]

    def save(self, product: Product) -> Product:
        """Guarda un producto nuevo o actualiza uno existente.

        Si ``product.id`` es ``None``, crea un registro nuevo. Si tiene ID,
        busca el registro existente y actualiza sus campos.

        Args:
            product (Product): Entidad del producto a persistir.

        Returns:
            Product: Entidad con ``id`` asignado tras la persistencia.
        """
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
        """Elimina un producto por su identificador.

        Args:
            product_id (int): Identificador del producto a eliminar.

        Returns:
            bool: ``True`` si se eliminó correctamente, ``False`` si no existía.
        """
        model = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not model:
            return False
        self.db.delete(model)
        self.db.commit()
        return True

    @staticmethod
    def _model_to_entity(model: ProductModel) -> Product:
        """Convierte un modelo ORM en entidad de dominio.

        Args:
            model (ProductModel): Modelo ORM de SQLAlchemy.

        Returns:
            Product: Entidad de dominio equivalente.
        """
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
        """Convierte una entidad de dominio en modelo ORM.

        Args:
            entity (Product): Entidad de dominio.

        Returns:
            ProductModel: Modelo ORM listo para persistir.
        """
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
