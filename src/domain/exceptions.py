"""Excepciones específicas del dominio.

Representan errores de negocio y permiten comunicar fallos
con mensajes claros desde el núcleo de la aplicación.
"""


class ProductNotFoundError(Exception):
    """Excepción lanzada cuando no se encuentra un producto."""

    def __init__(self, product_id: int | None = None, message: str | None = None) -> None:
        """Inicializa la excepción de producto no encontrado.

        Args:
            product_id: Identificador del producto buscado.
            message: Mensaje personalizado opcional.
        """
        default_message = (
            f"No se encontró el producto con id {product_id}."
            if product_id is not None
            else "No se encontró el producto solicitado."
        )
        super().__init__(message or default_message)


class InvalidProductDataError(Exception):
    """Excepción lanzada cuando los datos de un producto son inválidos."""

    def __init__(self, message: str = "Los datos del producto no son válidos.") -> None:
        """Inicializa la excepción de datos inválidos.

        Args:
            message: Mensaje descriptivo del error de validación.
        """
        super().__init__(message)


class ChatServiceError(Exception):
    """Excepción de negocio para errores del servicio de chat."""

    def __init__(self, message: str = "Ocurrió un error al procesar el chat.") -> None:
        """Inicializa la excepción del servicio de chat.

        Args:
            message: Mensaje del fallo.
        """
        super().__init__(message)
