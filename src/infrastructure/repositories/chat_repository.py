"""Repositorio SQLAlchemy para historial de chat.

Implementa el contrato ``IChatRepository`` del dominio utilizando
SQLAlchemy como ORM para persistir mensajes de conversación.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from src.domain.entities import ChatMessage
from src.domain.repositories import IChatRepository
from src.infrastructure.db.models import ChatMemoryModel


class SQLChatRepository(IChatRepository):
    """Implementación concreta de ``IChatRepository`` usando SQLAlchemy.

    Permite guardar, consultar y eliminar mensajes de conversación
    agrupados por sesión de usuario.

    Attributes:
        db (Session): Sesión activa de SQLAlchemy inyectada en el constructor.
    """

    def __init__(self, db: Session) -> None:
        """Inicializa el repositorio con una sesión de base de datos.

        Args:
            db (Session): Sesión activa de SQLAlchemy.
        """
        self.db = db

    def save_message(self, message: ChatMessage) -> ChatMessage:
        """Guarda un mensaje de chat en la base de datos.

        Args:
            message (ChatMessage): Entidad del mensaje a persistir.

        Returns:
            ChatMessage: El mensaje guardado con su ``id`` asignado.
        """
        model = self._entity_to_model(message)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._model_to_entity(model)

    def get_session_history(self, session_id: str, limit: int = 10) -> list[ChatMessage]:
        """Obtiene el historial cronológico de una sesión.

        Consulta los mensajes más recientes y los retorna en orden
        cronológico (del más antiguo al más reciente).

        Args:
            session_id (str): Identificador de la sesión.
            limit (int): Número máximo de mensajes a retornar. Por defecto 10.

        Returns:
            list[ChatMessage]: Lista de mensajes en orden cronológico.
        """
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
        """Elimina todos los mensajes de una sesión y retorna cuántos borró.

        Args:
            session_id (str): Identificador de la sesión a limpiar.

        Returns:
            int: Cantidad de mensajes eliminados.
        """
        deleted_count = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .delete()
        )
        self.db.commit()
        return int(deleted_count)

    def get_recent_messages(self, session_id: str, limit: int = 6) -> list[ChatMessage]:
        """Obtiene los mensajes más recientes de una sesión en orden cronológico.

        Crucial para construir el contexto conversacional que se envía
        al servicio de IA.

        Args:
            session_id (str): Identificador de la sesión.
            limit (int): Número máximo de mensajes recientes. Por defecto 6.

        Returns:
            list[ChatMessage]: Lista de mensajes recientes en orden cronológico.
        """
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
        """Convierte un modelo ORM en entidad de dominio.

        Args:
            model (ChatMemoryModel): Modelo ORM de SQLAlchemy.

        Returns:
            ChatMessage: Entidad de dominio equivalente.
        """
        return ChatMessage(
            id=model.id,
            session_id=model.session_id,
            role=model.role,
            message=model.message,
            timestamp=model.timestamp,
        )

    @staticmethod
    def _entity_to_model(entity: ChatMessage) -> ChatMemoryModel:
        """Convierte una entidad de dominio en modelo ORM.

        Args:
            entity (ChatMessage): Entidad de dominio.

        Returns:
            ChatMemoryModel: Modelo ORM listo para persistir.
        """
        return ChatMemoryModel(
            id=entity.id,
            session_id=entity.session_id,
            role=entity.role,
            message=entity.message,
            timestamp=entity.timestamp,
        )
