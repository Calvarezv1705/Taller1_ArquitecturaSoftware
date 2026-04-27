"""Configuración y utilidades de base de datos con SQLAlchemy.

Proporciona el motor de conexión, la factoría de sesiones y funciones
de utilidad para inicializar la base de datos y obtener sesiones en
los endpoints de FastAPI mediante inyección de dependencias.
"""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config import settings


def _resolve_database_url(database_url: str) -> str:
    """Resuelve rutas relativas de SQLite a una ruta absoluta del proyecto.

    Convierte URLs con prefijo ``sqlite:///./`` a rutas absolutas basadas
    en la raíz del proyecto, lo que evita problemas al ejecutar desde
    distintos directorios de trabajo.

    Args:
        database_url (str): URL de conexión de SQLAlchemy.

    Returns:
        str: URL resuelta. Si no es una ruta relativa de SQLite, se retorna sin cambios.
    """
    relative_prefix = "sqlite:///./"
    if not database_url.startswith(relative_prefix):
        return database_url

    project_root = Path(__file__).resolve().parents[3]
    relative_path = database_url.removeprefix(relative_prefix)
    absolute_path = project_root / relative_path
    return f"sqlite:///{absolute_path}"


resolved_database_url = _resolve_database_url(settings.database_url)

engine = create_engine(
    resolved_database_url,
    connect_args={"check_same_thread": False} if resolved_database_url.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator:
    """Entrega una sesión de base de datos para dependencias de FastAPI.

    Crea una sesión nueva con ``SessionLocal``, la entrega al endpoint
    mediante ``yield`` y la cierra automáticamente al finalizar el
    request, garantizando que no haya fugas de conexión.

    Yields:
        Session: Sesión activa de SQLAlchemy.

    Example:
        >>> @app.get("/ejemplo")
        ... def ejemplo(db: Session = Depends(get_db)):
        ...     return db.query(ProductModel).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Inicializa el esquema y los datos semilla de la base de datos.

    Crea todas las tablas definidas en los modelos ORM si no existen,
    y luego carga los datos iniciales de productos si la tabla está vacía.

    Note:
        Esta función se ejecuta automáticamente al iniciar la aplicación
        FastAPI mediante el evento ``startup``.
    """
    from . import models  # noqa: F401  # Import requerido por SQLAlchemy metadata
    from .init_data import load_initial_data

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        load_initial_data(db)
    finally:
        db.close()
