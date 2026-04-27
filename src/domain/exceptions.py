"""Excepciones específicas del dominio.

Representan errores de negocio y permiten comunicar fallos con mensajes
claros desde el núcleo de la aplicación. Al usar excepciones propias se
evita depender de excepciones genéricas de Python.
"""


class ProductNotFoundError(Exception):
    """Excepción lanzada cuando no se encuentra un producto solicitado.

    Attributes:
        message (str): Mensaje descriptivo del error.

    Args:
        product_id (int | None): Identificador del producto buscado.
        message (str | None): Mensaje personalizado opcional.

    Example:
        >>> raise ProductNotFoundError(product_id=42)
        ProductNotFoundError: No se encontró el producto con id 42.
    """

    def __init__(self, product_id: int | None = None, message: str | None = None) -> None:
        """Inicializa la excepción de producto no encontrado.

        Args:
            product_id (int | None): Identificador del producto buscado.
            message (str | None): Mensaje personalizado opcional.
        """
        default_message = (
            f"No se encontró el producto con id {product_id}."
            if product_id is not None
            else "No se encontró el producto solicitado."
        )
        self.message = message or default_message
        super().__init__(self.message)


class InvalidProductDataError(Exception):
    """Excepción lanzada cuando los datos de un producto son inválidos.

    Se usa para señalar errores de validación en la creación o
    actualización de productos.

    Attributes:
        message (str): Mensaje descriptivo del error de validación.

    Args:
        message (str): Mensaje descriptivo. Por defecto indica datos inválidos.

    Example:
        >>> raise InvalidProductDataError("El precio no puede ser negativo.")
        InvalidProductDataError: El precio no puede ser negativo.
    """

    def __init__(self, message: str = "Los datos del producto no son válidos.") -> None:
        """Inicializa la excepción de datos inválidos.

        Args:
            message (str): Mensaje descriptivo del error de validación.
        """
        self.message = message
        super().__init__(self.message)


class ChatServiceError(Exception):
    """Excepción de negocio para errores del servicio de chat.

    Se lanza cuando ocurre un error al procesar un mensaje de chat,
    ya sea en la comunicación con la IA o en la persistencia.

    Attributes:
        message (str): Mensaje descriptivo del fallo.

    Args:
        message (str): Mensaje del fallo. Por defecto indica error genérico.

    Example:
        >>> raise ChatServiceError("No se pudo conectar con Gemini.")
        ChatServiceError: No se pudo conectar con Gemini.
    """

    def __init__(self, message: str = "Ocurrió un error al procesar el chat.") -> None:
        """Inicializa la excepción del servicio de chat.

        Args:
            message (str): Mensaje del fallo.
        """
        self.message = message
        super().__init__(self.message)
