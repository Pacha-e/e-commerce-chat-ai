from rest_framework import serializers
from .models import Product, ChatMessage


class ProductSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Product. Expone todos los campos vía REST API."""

    class Meta:
        model = Product
        fields = ['id', 'name', 'brand', 'category', 'size', 'color',
                  'price', 'stock', 'description', 'image_url']


class ChatRequestSerializer(serializers.Serializer):
    """Serializador para la solicitud de mensaje al chat IA."""

    session_id = serializers.CharField(required=False, allow_blank=True,
                                       help_text="ID de sesión (se genera automáticamente si no se envía)")
    message = serializers.CharField(help_text="Mensaje del usuario al asistente")


class ChatResponseSerializer(serializers.Serializer):
    """Serializador para la respuesta del asistente IA."""

    assistant_message = serializers.CharField()
    timestamp = serializers.DateTimeField()
    session_id = serializers.CharField()


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializador para el historial de mensajes de chat."""

    class Meta:
        model = ChatMessage
        fields = ['role', 'message', 'timestamp']
