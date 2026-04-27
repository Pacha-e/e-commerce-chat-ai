import os
from google import genai
from typing import List
from dotenv import load_dotenv

from core_logic.domain.entities import Product, ChatMessage, ChatContext

load_dotenv()

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY", "")
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.0-flash"

    def generate_response(self, user_message: str, chat_history: List[ChatMessage], products: List[Product]) -> str:
        context = ChatContext(messages=chat_history)
        history_text = context.format_for_prompt()
        
        products_text = "\n".join([
            f"- {p.brand} {p.name}: {p.price} USD, Talla {p.size}. {p.description}"
            for p in products if p.stock > 0
        ])

        prompt = f"""
        Eres un asistente experto en ventas para una tienda de zapatos premium.
        Tu objetivo es ayudar al cliente a elegir el mejor zapato basándote en el catálogo.

        REGLAS:
        1. Sé amable, profesional y conciso.
        2. Solo recomienda productos que existan en el catálogo proporcionado.
        3. Si el usuario pregunta por algo que no tenemos, indicalo gentilmente y ofrece una alternativa.
        4. Usa el historial para mantener la coherencia.
        5. Siempre menciona el precio y la marca al recomendar.

        HISTORIAL DE CONVERSACIÓN:
        {history_text}

        CATÁLOGO DE PRODUCTOS DISPONIBLES:
        {products_text}

        MENSAJE DEL USUARIO:
        {user_message}

        RESPUESTA DEL ASISTENTE (en español):
        """

        try:
            response = self.client.models.generate_content(model=self.model_name, contents=prompt)
            return response.text.strip()
        except Exception as e:
            error_msg = str(e).lower()
            # Si el error es por cuota (429), usamos el modo de respaldo local
            if "429" in error_msg or "quota" in error_msg:
                # Buscamos palabras clave en el mensaje del usuario
                query = user_message.lower()
                matches = [p for p in products if p.brand.lower() in query or p.name.lower() in query or p.category.lower() in query]
                
                if matches:
                    res = "¡Hola! Mi conexión con el 'cerebro' de Google está saturada, pero como soy un asistente experto, puedo decirte que tengo estos modelos para ti según lo que buscas:\n\n"
                    for p in matches[:3]:
                        res += f"✅ {p.brand} {p.name} por solo ${p.price}. {p.description}\n"
                    res += "\n¿Te gustaría ver alguno en detalle?"
                    return res
                else:
                    return "¡Hola! Mi conexión con Google está saturada temporalmente. Tengo un catálogo de 10 productos Nike, Adidas y Puma. ¿Buscas alguna marca en especial para ayudarte?"
            
            return f"Lo siento, tuve un problema al procesar tu solicitud. error: {str(e)}"
