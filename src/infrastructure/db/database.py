"""Configuración y utilidades de base de datos con SQLAlchemy."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config import settings


def _resolve_database_url(database_url: str) -> str:
    """Resuelve rutas relativas de SQLite a una ruta absoluta del proyecto."""
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

    Yields:
        Sesión activa de SQLAlchemy.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Inicializa esquema y datos semilla de la base de datos."""
    from . import models  # noqa: F401  # Import requerido por SQLAlchemy metadata
    from .init_data import load_initial_data

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        load_initial_data(db)
    finally:
        db.close()
