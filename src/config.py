"""Configuración global de la aplicación.

Centraliza lectura de variables de entorno para evitar valores hardcodeados.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Objeto de configuración inmutable para toda la aplicación."""

    app_name: str = "E-commerce Chat IA"
    app_version: str = "1.0.0"
    environment: str = os.getenv("ENVIRONMENT", "development")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/ecommerce_chat.db")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


settings = Settings()
