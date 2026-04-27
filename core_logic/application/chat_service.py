"""
Servicio de aplicación para el chat con IA.

Orquesta la interacción entre el repositorio de productos, el repositorio
de chat y el servicio de IA de Gemini para proporcionar respuestas
contextuales a los usuarios del e-commerce.
"""
from typing import List, Any
from datetime import datetime
from core_logic.domain.entities import ChatMessage, ChatContext
from core_logic.domain.repositories import IProductRepository, IChatRepository
from core_logic.domain.exceptions import ChatServiceError
from core_logic.application.dtos import ChatMessageRequestDTO, ChatMessageResponseDTO, ChatHistoryDTO


class ChatService:
    """
    Servicio de aplicación para gestionar el chat con IA.

    Este servicio orquesta la interacción entre el repositorio de productos,
    el repositorio de chat y el servicio de IA de Gemini para proporcionar
    respuestas contextuales a los usuarios.

    Attributes:
        product_repo (IProductRepository): Repositorio de productos.
        chat_repo (IChatRepository): Repositorio de mensajes de chat.
        ai_service (Any): Servicio de IA de Google Gemini.

    Example:
        >>> service = ChatService(product_repo, chat_repo, gemini_service)
        >>> request = ChatMessageRequestDTO(session_id="user1", message="Hola")
        >>> response = service.process_message(request)
    """

    def __init__(
        self,
        product_repo: IProductRepository,
        chat_repo: IChatRepository,
        ai_service: Any
    ):
        """
        Inicializa el servicio con las dependencias necesarias.

        Args:
            product_repo (IProductRepository): Repositorio de productos.
            chat_repo (IChatRepository): Repositorio de chat.
            ai_service (GeminiService): Servicio de IA.
        """
        self.product_repo = product_repo
        self.chat_repo = chat_repo
        self.ai_service = ai_service

    def process_message(self, request: ChatMessageRequestDTO) -> ChatMessageResponseDTO:
        """
        Procesa un mensaje del usuario y genera una respuesta con IA.

        Flujo completo:
        1. Obtiene los productos disponibles del repositorio.
        2. Recupera el historial reciente de la sesión (últimos 6 mensajes).
        3. Crea el contexto conversacional con el historial.
        4. Envía el mensaje, productos y contexto a Gemini para generar respuesta.
        5. Guarda el mensaje del usuario en la base de datos.
        6. Guarda la respuesta del asistente en la base de datos.
        7. Retorna la respuesta formateada como DTO.

        Args:
            request (ChatMessageRequestDTO): Mensaje del usuario con session_id.

        Returns:
            ChatMessageResponseDTO: Respuesta generada por la IA con timestamp.

        Raises:
            ChatServiceError: Si hay un error al procesar el mensaje o
                comunicarse con el servicio de IA.

        Example:
            >>> request = ChatMessageRequestDTO(
            ...     session_id="user123",
            ...     message="Busco zapatos Nike para correr"
            ... )
            >>> response = chat_service.process_message(request)
            >>> print(response.assistant_message)
            "Tengo varios modelos Nike disponibles..."
        """
        try:
            products = self.product_repo.get_all()

            recent_messages = self.chat_repo.get_recent_messages(
                session_id=request.session_id,
                count=6
            )

            context = ChatContext(messages=recent_messages)

            assistant_response = self.ai_service.generate_response(
                user_message=request.message,
                products=products,
                chat_history=context.get_recent_messages()
            )

            now = datetime.utcnow()

            user_msg = ChatMessage(
                id=None,
                session_id=request.session_id,
                role="user",
                message=request.message,
                timestamp=now
            )
            self.chat_repo.save_message(user_msg)

            assistant_msg = ChatMessage(
                id=None,
                session_id=request.session_id,
                role="assistant",
                message=assistant_response,
                timestamp=now
            )
            self.chat_repo.save_message(assistant_msg)

            return ChatMessageResponseDTO(
                session_id=request.session_id,
                user_message=request.message,
                assistant_message=assistant_response,
                timestamp=now
            )

        except ChatServiceError:
            raise
        except Exception as e:
            raise ChatServiceError(f"Error procesando mensaje: {str(e)}")

    def get_session_history(self, session_id: str, limit: int = 10) -> List[ChatHistoryDTO]:
        """
        Obtiene el historial de mensajes de una sesión de chat.

        Args:
            session_id (str): Identificador de la sesión.
            limit (int): Número máximo de mensajes a retornar (default: 10).

        Returns:
            List[ChatHistoryDTO]: Lista de mensajes del historial.
        """
        messages = self.chat_repo.get_session_history(
            session_id=session_id,
            limit=limit
        )
        return [
            ChatHistoryDTO(
                id=msg.id,
                role=msg.role,
                message=msg.message,
                timestamp=msg.timestamp
            )
            for msg in messages
        ]

    def clear_session_history(self, session_id: str) -> int:
        """
        Elimina todo el historial de una sesión de chat.

        Args:
            session_id (str): Identificador de la sesión a limpiar.

        Returns:
            int: Cantidad de mensajes eliminados.
        """
        return self.chat_repo.delete_session_history(session_id)
