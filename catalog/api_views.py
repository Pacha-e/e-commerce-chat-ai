import uuid
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample

from core_logic.application.dtos import ChatMessageRequestDTO
from .repositories import DjangoProductRepository, DjangoChatRepository
from .ai_service import GeminiService
from .serializers import (
    ProductSerializer, ChatRequestSerializer,
    ChatResponseSerializer, ChatMessageSerializer,
)
from .models import Product, ChatMessage


def _get_services():
    """Instancia los servicios de aplicación con repositorios Django."""
    from core_logic.application.product_service import ProductService
    from core_logic.application.chat_service import ChatService
    product_repo = DjangoProductRepository()
    chat_repo = DjangoChatRepository()
    product_service = ProductService(product_repo)
    chat_service = ChatService(product_repo, chat_repo, GeminiService())
    return product_service, chat_service


class ProductListAPIView(APIView):
    """
    Endpoint REST para listar todos los productos disponibles en la tienda.

    Permite consultar el catálogo completo de zapatos con stock disponible.
    """

    @extend_schema(
        summary="Listar productos",
        description="Retorna el catálogo completo de zapatos disponibles.",
        responses={200: ProductSerializer(many=True)},
        tags=["Productos"],
    )
    def get(self, request):
        """Retorna todos los productos de la tienda ordenados por marca."""
        products = Product.objects.all().order_by('brand', 'name')
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductDetailAPIView(APIView):
    """Endpoint REST para consultar un producto específico por su ID."""

    @extend_schema(
        summary="Detalle de producto",
        description="Retorna los datos completos de un producto por ID.",
        responses={200: ProductSerializer, 404: None},
        tags=["Productos"],
    )
    def get(self, request, pk):
        """Retorna un producto por ID o 404 si no existe."""
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ProductSerializer(product).data)


class ChatAPIView(APIView):
    """
    Endpoint REST para enviar mensajes al asistente IA de la tienda.

    El asistente usa Google Gemini 2.0 Flash para generar respuestas
    contextuales basadas en el catálogo de productos disponibles.
    """

    @extend_schema(
        summary="Enviar mensaje al chat IA",
        description=(
            "Envía un mensaje al asistente de IA. "
            "Si no se proporciona session_id, se genera uno automáticamente. "
            "El asistente recuerda el historial de la sesión."
        ),
        request=ChatRequestSerializer,
        responses={200: ChatResponseSerializer, 400: None},
        examples=[
            OpenApiExample(
                "Consulta de zapatos Nike",
                value={"message": "Tienes Nike para running?", "session_id": "abc-123"},
                request_only=True,
            )
        ],
        tags=["Chat IA"],
    )
    def post(self, request):
        """Procesa el mensaje del usuario y retorna la respuesta del asistente."""
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        message = serializer.validated_data['message']
        session_id = serializer.validated_data.get('session_id') or str(uuid.uuid4())

        _, chat_service = _get_services()
        dto = ChatMessageRequestDTO(session_id=session_id, message=message)
        resp = chat_service.process_message(dto)

        return Response({
            'assistant_message': resp.assistant_message,
            'timestamp': resp.timestamp.isoformat(),
            'session_id': session_id,
        })


class ChatHistoryAPIView(APIView):
    """Endpoint REST para consultar el historial de una sesión de chat."""

    @extend_schema(
        summary="Historial de chat",
        description="Retorna todos los mensajes de una sesión de chat ordenados por tiempo.",
        responses={200: ChatMessageSerializer(many=True)},
        tags=["Chat IA"],
    )
    def get(self, request, session_id):
        """Retorna el historial de mensajes de la sesión indicada."""
        messages = ChatMessage.objects.filter(session_id=session_id).order_by('timestamp')
        return Response(ChatMessageSerializer(messages, many=True).data)
