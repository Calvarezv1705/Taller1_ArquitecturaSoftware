"""Configuración y utilidades de base de datos con SQLAlchemy."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
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
