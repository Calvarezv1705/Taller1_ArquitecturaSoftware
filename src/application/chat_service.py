"""Casos de uso para chat conversacional con IA."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol

from .dtos import ChatHistoryDTO, ChatMessageRequestDTO, ChatMessageResponseDTO
from ..domain.entities import ChatContext, ChatMessage
from ..domain.exceptions import ChatServiceError
from ..domain.repositories import IChatRepository, IProductRepository


class IAProvider(Protocol):
    """Contrato de proveedor de IA para desacoplar la capa de aplicación."""

    async def generate_response(
        self,
        user_message: str,
        products: list,
        context: ChatContext,
    ) -> str:
        """Genera una respuesta textual para el usuario."""


class ChatService:
    """Servicio de aplicación que orquesta la conversación con IA."""

    def __init__(
        self,
        product_repository: IProductRepository,
        chat_repository: IChatRepository,
        ai_service: IAProvider | None = None,
    ) -> None:
        """Inicializa dependencias del caso de uso de chat."""
        self.product_repository = product_repository
        self.chat_repository = chat_repository
        self.ai_service = ai_service

    async def process_message(self, request: ChatMessageRequestDTO) -> ChatMessageResponseDTO:
        """Procesa un mensaje del usuario y retorna la respuesta del asistente.

        Args:
            request: DTO con `session_id` y mensaje del usuario.

        Returns:
            DTO con respuesta del asistente y marca de tiempo.

        Raises:
            ChatServiceError: Si ocurre un error durante el procesamiento.
        """
        try:
            if self.ai_service is None:
                raise ChatServiceError("No se configuró un proveedor de IA.")

            products = self.product_repository.get_all()
            recent_messages = self.chat_repository.get_recent_messages(request.session_id, limit=6)
            context = ChatContext(messages=recent_messages)

            assistant_text = await self.ai_service.generate_response(
                user_message=request.message,
                products=products,
                context=context,
            )

            user_msg = ChatMessage(
                session_id=request.session_id,
                role="user",
                message=request.message,
                timestamp=datetime.now(UTC),
            )
            assistant_msg = ChatMessage(
                session_id=request.session_id,
                role="assistant",
                message=assistant_text,
                timestamp=datetime.now(UTC),
            )

            self.chat_repository.save_message(user_msg)
            self.chat_repository.save_message(assistant_msg)

            return ChatMessageResponseDTO(
                session_id=request.session_id,
                user_message=request.message,
                assistant_message=assistant_text,
                timestamp=assistant_msg.timestamp,
            )
        except Exception as exc:  # noqa: BLE001
            raise ChatServiceError(f"No fue posible procesar el mensaje: {exc}") from exc

    def get_session_history(self, session_id: str, limit: int = 10) -> list[ChatHistoryDTO]:
        """Obtiene el historial de una sesión en formato DTO."""
        history = self.chat_repository.get_session_history(session_id=session_id, limit=limit)
        return [ChatHistoryDTO.model_validate(message) for message in history]

    def clear_session_history(self, session_id: str) -> int:
        """Elimina el historial completo de una sesión.

        Returns:
            Cantidad de mensajes eliminados.
        """
        return self.chat_repository.delete_session_history(session_id=session_id)
