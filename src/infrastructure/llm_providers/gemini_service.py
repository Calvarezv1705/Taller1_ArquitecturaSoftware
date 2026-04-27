"""Integración con Google Gemini para respuestas conversacionales."""

from __future__ import annotations

import asyncio

import google.generativeai as genai

from src.config import settings
from src.domain.entities import ChatContext, Product


class GeminiService:
    """Servicio de infraestructura para generar respuestas con Gemini."""

    def __init__(self) -> None:
        """Configura el cliente de Gemini a partir de variables de entorno."""
        if not settings.gemini_api_key:
            raise ValueError("No se encontró GEMINI_API_KEY en el entorno.")
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)

    def format_products_info(self, products: list[Product]) -> str:
        """Formatea el catálogo para incluirlo en el prompt."""
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
        """Genera una respuesta usando Gemini con catálogo y contexto.

        Args:
            user_message: Mensaje actual del usuario.
            products: Catálogo disponible.
            context: Contexto reciente de conversación.

        Returns:
            Texto generado por el asistente.
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
