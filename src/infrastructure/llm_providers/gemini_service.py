"""Integración con Google Gemini para respuestas conversacionales.

Proporciona el servicio ``GeminiService`` que se conecta a la API de
Google Gemini para generar respuestas contextuales basadas en el
catálogo de productos y el historial de conversación.
"""

from __future__ import annotations

import asyncio

import google.generativeai as genai

from src.config import settings
from src.domain.entities import ChatContext, Product


class GeminiService:
    """Servicio de infraestructura para generar respuestas con Google Gemini.

    Construye un prompt con el catálogo de productos y el contexto
    conversacional, y lo envía al modelo de IA para obtener una
    respuesta contextual.

    Attributes:
        model: Instancia del modelo generativo de Gemini configurado.

    Example:
        >>> service = GeminiService()
        >>> respuesta = await service.generate_response(
        ...     user_message="Busco zapatos Nike",
        ...     products=[...],
        ...     context=chat_context,
        ... )
    """

    def __init__(self) -> None:
        """Configura el cliente de Gemini a partir de variables de entorno.

        Raises:
            ValueError: Si la variable ``GEMINI_API_KEY`` no está configurada.
        """
        if not settings.gemini_api_key:
            raise ValueError("No se encontró GEMINI_API_KEY en el entorno.")
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)

    def format_products_info(self, products: list[Product]) -> str:
        """Formatea el catálogo de productos para incluirlo en el prompt.

        Cada producto se representa en una línea con nombre, marca,
        categoría, talla, color, precio y stock disponible.

        Args:
            products (list[Product]): Lista de entidades de producto.

        Returns:
            str: Texto formateado con la información de todos los productos,
                o un mensaje indicando que no hay productos disponibles.

        Example:
            >>> texto = service.format_products_info(productos)
            >>> print(texto)
            '- Air Zoom Pegasus 40 | Marca: Nike | ...'
        """
        if not products:
            return "No hay productos disponibles en este momento."

        lines: list[str] = []
        for product in products:
            lines.append(
                "- "
                f"{product.name} | Marca: {product.brand} | Categoría: {product.category} | "
                f"Talla: {product.size} | Color: {product.color} | "
                f"Precio: ${product.price:.2f} | Stock: {product.stock}"
            )
        return "\n".join(lines)

    async def generate_response(
        self,
        user_message: str,
        products: list[Product],
        context: ChatContext,
    ) -> str:
        """Genera una respuesta del asistente usando Gemini con catálogo y contexto.

        Construye un prompt completo con las instrucciones del sistema,
        la lista de productos disponibles, el historial conversacional
        y el mensaje actual del usuario, y lo envía a la API de Gemini.

        Args:
            user_message (str): Mensaje actual del usuario.
            products (list[Product]): Catálogo de productos disponibles.
            context (ChatContext): Contexto conversacional con mensajes recientes.

        Returns:
            str: Texto de respuesta generado por el modelo de IA. Si ocurre
                un error, retorna un mensaje informativo.
        """
        products_text = self.format_products_info(products)
        context_text = context.format_for_prompt(limit=6)

        prompt = f"""
Eres un asistente virtual experto en ventas de zapatos para un e-commerce.
Tu objetivo es ayudar a los clientes a encontrar los zapatos perfectos.

PRODUCTOS DISPONIBLES:
{products_text}

INSTRUCCIONES:
- Sé amigable y profesional.
- Usa el contexto de la conversación anterior.
- Recomienda productos específicos cuando sea apropiado.
- Menciona precios, tallas y disponibilidad real de stock.
- Si no tienes información suficiente, sé honesto.

HISTORIAL DE LA CONVERSACIÓN:
{context_text}

Usuario: {user_message}
Asistente:
        """.strip()

        try:
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            text = getattr(response, "text", None)
            if not text:
                return "No pude generar una respuesta en este momento. Intenta nuevamente."
            return text.strip()
        except Exception as exc:  # noqa: BLE001
            return f"Ocurrió un error al consultar Gemini: {exc}"
