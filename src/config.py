"""Configuración global de la aplicación.

Centraliza la lectura de variables de entorno para evitar valores
hardcodeados a lo largo del código. Se expone un objeto ``settings``
inmutable que el resto de módulos puede importar directamente.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Objeto de configuración inmutable para toda la aplicación.

    Carga valores de las variables de entorno una sola vez al inicio
    y los expone como atributos de solo lectura.

    Attributes:
        app_name (str): Nombre público de la aplicación mostrado en Swagger.
        app_version (str): Versión semántica del servicio.
        environment (str): Entorno de ejecución (``development``, ``production``, ``test``).
        database_url (str): Cadena de conexión SQLAlchemy a la base de datos.
        gemini_api_key (str): Clave de API de Google Gemini para el chat con IA.
        gemini_model (str): Nombre del modelo de Gemini a utilizar.
    """

    app_name: str = "E-commerce Chat IA"
    app_version: str = "1.0.0"
    environment: str = os.getenv("ENVIRONMENT", "development")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/ecommerce_chat.db")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


settings = Settings()
