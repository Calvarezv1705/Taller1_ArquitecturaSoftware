"""Casos de uso para gestión de productos.

Este módulo contiene el servicio de aplicación ``ProductService``, que
orquesta las operaciones de negocio sobre productos utilizando el
repositorio inyectado, siguiendo el patrón *Service Layer*.
"""

from __future__ import annotations

from .dtos import ProductDTO
from ..domain.entities import Product
from ..domain.exceptions import ProductNotFoundError
from ..domain.repositories import IProductRepository


class ProductService:
    """Servicio de aplicación para operaciones de productos.

    Orquesta las interacciones entre los endpoints de la API y el
    repositorio de productos, aplicando reglas de negocio y
    convirtiendo entre DTOs y entidades del dominio.

    Attributes:
        product_repository (IProductRepository): Repositorio de productos
            inyectado por dependencia.

    Example:
        >>> service = ProductService(product_repository=mi_repo)
        >>> productos = service.get_all_products()
    """

    def __init__(self, product_repository: IProductRepository) -> None:
        """Inicializa el servicio con el repositorio de productos.

        Args:
            product_repository (IProductRepository): Instancia del repositorio
                que implementa el contrato de acceso a datos de productos.
        """
        self.product_repository = product_repository

    def get_all_products(self) -> list[ProductDTO]:
        """Obtiene todos los productos del catálogo.

        Returns:
            list[ProductDTO]: Lista de DTOs con la información de todos los productos.
        """
        products = self.product_repository.get_all()
        return [ProductDTO.model_validate(product) for product in products]

    def get_product_by_id(self, product_id: int) -> ProductDTO:
        """Obtiene un producto por su identificador. Falla si no existe.

        Args:
            product_id (int): Identificador del producto buscado.

        Returns:
            ProductDTO: DTO con los datos del producto encontrado.

        Raises:
            ProductNotFoundError: Si no existe un producto con el ID dado.

        Example:
            >>> dto = service.get_product_by_id(1)
            >>> print(dto.name)
            'Air Zoom Pegasus 40'
        """
        product = self.product_repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(product_id=product_id)
        return ProductDTO.model_validate(product)

    def search_products(self, brand: str | None = None, category: str | None = None) -> list[ProductDTO]:
        """Busca productos aplicando filtros opcionales de marca y categoría.

        Si se proporcionan ambos filtros, primero filtra por marca y luego
        por categoría en memoria. Si solo se proporciona uno, se delega
        al repositorio.

        Args:
            brand (str | None): Marca a filtrar. ``None`` para no filtrar por marca.
            category (str | None): Categoría a filtrar. ``None`` para no filtrar por categoría.

        Returns:
            list[ProductDTO]: Lista de DTOs que coinciden con los filtros aplicados.
        """
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
        """Crea un producto nuevo en el catálogo.

        Convierte el DTO a entidad de dominio (ejecutando validaciones)
        y lo persiste mediante el repositorio.

        Args:
            product_dto (ProductDTO): DTO con los datos del nuevo producto.

        Returns:
            ProductDTO: DTO del producto creado con su ``id`` asignado.

        Example:
            >>> dto = ProductDTO(name="Nuevo", brand="Nike", category="Running",
            ...     size="42", color="Negro", price=100.0, stock=5)
            >>> creado = service.create_product(dto)
            >>> print(creado.id)
            11
        """
        product = Product(**product_dto.model_dump(exclude={"id"}))
        saved = self.product_repository.save(product)
        return ProductDTO.model_validate(saved)

    def update_product(self, product_id: int, product_dto: ProductDTO) -> ProductDTO:
        """Actualiza un producto existente por su identificador.

        Verifica que el producto exista antes de actualizar.

        Args:
            product_id (int): Identificador del producto a actualizar.
            product_dto (ProductDTO): DTO con los nuevos datos del producto.

        Returns:
            ProductDTO: DTO del producto actualizado.

        Raises:
            ProductNotFoundError: Si no existe un producto con el ID dado.
        """
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
        """Elimina un producto del catálogo. Lanza error si no existe.

        Args:
            product_id (int): Identificador del producto a eliminar.

        Returns:
            bool: ``True`` si se eliminó correctamente.

        Raises:
            ProductNotFoundError: Si no existe un producto con el ID dado.
        """
        existing = self.product_repository.get_by_id(product_id)
        if existing is None:
            raise ProductNotFoundError(product_id=product_id)
        return self.product_repository.delete(product_id)

    def get_available_products(self) -> list[ProductDTO]:
        """Retorna solo productos con stock mayor que cero.

        Útil para mostrar al usuario únicamente los productos que puede
        comprar en ese momento.

        Returns:
            list[ProductDTO]: Lista de DTOs de productos disponibles.
        """
        products = self.product_repository.get_all()
        available = [product for product in products if product.is_available()]
        return [ProductDTO.model_validate(product) for product in available]
