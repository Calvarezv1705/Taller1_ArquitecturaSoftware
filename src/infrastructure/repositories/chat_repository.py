"""Repositorio SQLAlchemy para historial de chat."""

from __future__ import annotations

from sqlalchemy.orm import Session

from src.domain.entities import ChatMessage
from src.domain.repositories import IChatRepository
from src.infrastructure.db.models import ChatMemoryModel


class SQLChatRepository(IChatRepository):
    """Implementación concreta de `IChatRepository` usando SQLAlchemy."""

    def __init__(self, db: Session) -> None:
        """Inicializa el repositorio con sesión de base de datos."""
        self.db = db

    def save_message(self, message: ChatMessage) -> ChatMessage:
        """Guarda un mensaje de chat."""
        model = self._entity_to_model(message)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._model_to_entity(model)

    def get_session_history(self, session_id: str, limit: int = 10) -> list[ChatMessage]:
        """Obtiene historial cronológico de una sesión."""
        query = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .order_by(ChatMemoryModel.timestamp.desc())
            .limit(limit)
        )
        models = query.all()
        models.reverse()
        return [self._model_to_entity(model) for model in models]

    def delete_session_history(self, session_id: str) -> int:
        """Elimina todos los mensajes de una sesión y retorna cuántos borró."""
        deleted_count = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .delete()
        )
        self.db.commit()
        return int(deleted_count)

    def get_recent_messages(self, session_id: str, limit: int = 6) -> list[ChatMessage]:
        """Obtiene los mensajes más recientes en orden cronológico."""
        query = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .order_by(ChatMemoryModel.timestamp.desc())
            .limit(limit)
        )
        models = query.all()
        models.reverse()
        return [self._model_to_entity(model) for model in models]

    @staticmethod
    def _model_to_entity(model: ChatMemoryModel) -> ChatMessage:
        """Convierte un modelo ORM en entidad de dominio."""
        return ChatMessage(
            id=model.id,
            session_id=model.session_id,
            role=model.role,
            message=model.message,
            timestamp=model.timestamp,
        )

    @staticmethod
    def _entity_to_model(entity: ChatMessage) -> ChatMemoryModel:
        """Convierte una entidad de dominio en modelo ORM."""
        return ChatMemoryModel(
            id=entity.id,
            session_id=entity.session_id,
            role=entity.role,
            message=entity.message,
            timestamp=entity.timestamp,
        )
