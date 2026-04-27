"""Casos de uso para chat conversacional con IA.

Este módulo contiene el servicio ``ChatService`` que orquesta la interacción
entre el repositorio de productos, el repositorio de chat y el proveedor
de inteligencia artificial para generar respuestas contextuales.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol

from .dtos import ChatHistoryDTO, ChatMessageRequestDTO, ChatMessageResponseDTO
from ..domain.entities import ChatContext, ChatMessage
from ..domain.exceptions import ChatServiceError
from ..domain.repositories import IChatRepository, IProductRepository


class IAProvider(Protocol):
    """Contrato (protocolo) de proveedor de IA para desacoplar la capa de aplicación.

    Cualquier servicio de IA (Gemini, OpenAI, etc.) debe cumplir con este
    protocolo para poder ser usado por ``ChatService``.
    """

    async def generate_response(
        self,
        user_message: str,
        products: list,
        context: ChatContext,
    ) -> str:
        """Genera una respuesta textual para el usuario.

        Args:
            user_message (str): Mensaje actual del usuario.
            products (list): Lista de productos disponibles para contexto.
            context (ChatContext): Contexto conversacional reciente.

        Returns:
            str: Texto de respuesta generado por el modelo de IA.
        """


class ChatService:
    """Servicio de aplicación que orquesta la conversación con IA.

    Coordina la obtención de productos disponibles, la recuperación del
    historial conversacional, la generación de respuestas con IA y la
    persistencia de los mensajes.

    Attributes:
        product_repository (IProductRepository): Repositorio de productos
            para obtener el catálogo disponible.
        chat_repository (IChatRepository): Repositorio de mensajes de chat
            para persistir y recuperar el historial.
        ai_service (IAProvider | None): Proveedor de IA para generar respuestas.

    Example:
        >>> service = ChatService(product_repo, chat_repo, gemini_service)
        >>> response = await service.process_message(request_dto)
    """

    def __init__(
        self,
        product_repository: IProductRepository,
        chat_repository: IChatRepository,
        ai_service: IAProvider | None = None,
    ) -> None:
        """Inicializa las dependencias del caso de uso de chat.

        Args:
            product_repository (IProductRepository): Repositorio de productos.
            chat_repository (IChatRepository): Repositorio de mensajes de chat.
            ai_service (IAProvider | None): Proveedor de IA. Si es ``None``,
                el servicio lanzará error al intentar procesar mensajes.
        """
        self.product_repository = product_repository
        self.chat_repository = chat_repository
        self.ai_service = ai_service

    async def process_message(self, request: ChatMessageRequestDTO) -> ChatMessageResponseDTO:
        """Procesa un mensaje del usuario y retorna la respuesta del asistente.

        Flujo completo del caso de uso:
        1. Obtiene todos los productos del catálogo.
        2. Recupera los últimos 6 mensajes de la sesión.
        3. Crea el contexto conversacional.
        4. Genera la respuesta con el proveedor de IA.
        5. Guarda el mensaje del usuario y la respuesta del asistente.
        6. Retorna el DTO de respuesta.

        Args:
            request (ChatMessageRequestDTO): DTO con ``session_id`` y mensaje del usuario.

        Returns:
            ChatMessageResponseDTO: DTO con la respuesta del asistente y marca de tiempo.

        Raises:
            ChatServiceError: Si no hay proveedor de IA configurado o si
                ocurre un error durante el procesamiento.

        Example:
            >>> request = ChatMessageRequestDTO(
            ...     session_id="user123", message="Busco zapatos Nike"
            ... )
            >>> response = await chat_service.process_message(request)
            >>> print(response.assistant_message)
            'Tengo varios modelos Nike disponibles...'
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
        """Obtiene el historial de una sesión en formato DTO.

        Args:
            session_id (str): Identificador de la sesión a consultar.
            limit (int): Número máximo de mensajes a retornar. Por defecto 10.

        Returns:
            list[ChatHistoryDTO]: Lista de DTOs de mensajes en orden cronológico.
        """
        history = self.chat_repository.get_session_history(session_id=session_id, limit=limit)
        return [ChatHistoryDTO.model_validate(message) for message in history]

    def clear_session_history(self, session_id: str) -> int:
        """Elimina el historial completo de una sesión.

        Args:
            session_id (str): Identificador de la sesión a limpiar.

        Returns:
            int: Cantidad de mensajes eliminados.
        """
        return self.chat_repository.delete_session_history(session_id=session_id)
