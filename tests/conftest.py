"""Configuraciones compartidas de pytest."""

from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def ensure_env_for_tests(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Asegura variables de entorno mínimas durante pruebas."""
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", "dummy"))
