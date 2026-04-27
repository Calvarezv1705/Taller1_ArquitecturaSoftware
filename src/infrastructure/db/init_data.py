"""Carga de datos semilla para el catálogo de productos.

Define una lista de 10 productos iniciales realistas y variados,
y proporciona una función para insertarlos en la base de datos
si la tabla de productos está vacía.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from .models import ProductModel

INITIAL_PRODUCTS: list[dict] = [
    {
        "name": "Air Zoom Pegasus 40",
        "brand": "Nike",
        "category": "Running",
        "size": "42",
        "color": "Negro",
        "price": 120.0,
        "stock": 5,
        "description": "Tenis de running con gran amortiguación y respuesta.",
    },
    {
        "name": "Ultraboost 21",
        "brand": "Adidas",
        "category": "Running",
        "size": "41",
        "color": "Blanco",
        "price": 150.0,
        "stock": 3,
        "description": "Tenis de alto retorno de energía para largas distancias.",
    },
    {
        "name": "Suede Classic",
        "brand": "Puma",
        "category": "Casual",
        "size": "40",
        "color": "Azul",
        "price": 80.0,
        "stock": 10,
        "description": "Modelo clásico urbano para uso diario.",
    },
    {
        "name": "Chuck Taylor All Star",
        "brand": "Converse",
        "category": "Casual",
        "size": "42",
        "color": "Rojo",
        "price": 70.0,
        "stock": 8,
        "description": "Tenis icónicos de lona para estilo casual.",
    },
    {
        "name": "Gel-Kayano 30",
        "brand": "Asics",
        "category": "Running",
        "size": "43",
        "color": "Gris",
        "price": 170.0,
        "stock": 4,
        "description": "Estabilidad premium para pronadores y entrenamientos largos.",
    },
    {
        "name": "574 Core",
        "brand": "New Balance",
        "category": "Casual",
        "size": "41",
        "color": "Gris",
        "price": 95.0,
        "stock": 6,
        "description": "Comodidad y diseño retro versátil.",
    },
    {
        "name": "Cloud 5",
        "brand": "On",
        "category": "Running",
        "size": "42",
        "color": "Blanco",
        "price": 160.0,
        "stock": 7,
        "description": "Tenis livianos con tecnología CloudTec.",
    },
    {
        "name": "Oxford Leather",
        "brand": "Clarks",
        "category": "Formal",
        "size": "42",
        "color": "Café",
        "price": 110.0,
        "stock": 5,
        "description": "Zapato formal de cuero para oficina y eventos.",
    },
    {
        "name": "Derby Elegance",
        "brand": "Hush Puppies",
        "category": "Formal",
        "size": "43",
        "color": "Negro",
        "price": 130.0,
        "stock": 2,
        "description": "Zapato formal cómodo con plantilla acolchada.",
    },
    {
        "name": "RS-X",
        "brand": "Puma",
        "category": "Casual",
        "size": "41",
        "color": "Multicolor",
        "price": 105.0,
        "stock": 9,
        "description": "Tenis lifestyle con diseño moderno y llamativo.",
    },
]
"""list[dict]: Datos semilla con 10 productos variados de distintas marcas,
categorías, tallas y rangos de precio ($70 - $170).
"""


def load_initial_data(db: Session) -> None:
    """Carga los datos iniciales del catálogo si la tabla de productos está vacía.

    Verifica la cantidad de registros existentes y, solo si es cero,
    inserta los 10 productos definidos en ``INITIAL_PRODUCTS``.

    Args:
        db (Session): Sesión activa de SQLAlchemy.

    Note:
        Esta función es idempotente: si ya existen productos no realiza
        ninguna inserción.
    """
    existing_count = db.query(ProductModel).count()
    if existing_count > 0:
        return

    seed_models = [ProductModel(**product_data) for product_data in INITIAL_PRODUCTS]
    db.add_all(seed_models)
    db.commit()
