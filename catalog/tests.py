"""
Tests para la app catalog: modelos, vistas HTML, API REST y capa de dominio.
Cobertura objetivo: >60%.
"""
import json
import uuid
from unittest.mock import MagicMock, patch
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Product, ChatMessage
from .serializers import ProductSerializer, ChatRequestSerializer
from core_logic.domain.entities import (
    Product as ProductEntity, ChatMessage as ChatMessageEntity, ChatContext,
)
from core_logic.application.dtos import ChatMessageRequestDTO, ProductDTO


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_product(**kwargs):
    """Crea un producto en base de datos con valores por defecto."""
    defaults = dict(
        name="Air Max Test", brand="Nike", category="Running",
        size="42", color="Negro", price="120.00", stock=5,
        description="Zapato de prueba.", image_url="https://example.com/img.jpg",
    )
    defaults.update(kwargs)
    return Product.objects.create(**defaults)


# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------

class ProductModelTest(TestCase):
    """Pruebas del modelo Product."""

    def test_str_representation(self):
        """El __str__ debe retornar 'Nombre (Marca)'."""
        p = _make_product()
        self.assertEqual(str(p), "Air Max Test (Nike)")

    def test_create_with_all_fields(self):
        """Verifica que todos los campos se persisten correctamente."""
        p = _make_product(name="Stan Smith", brand="Adidas", stock=10)
        self.assertEqual(p.brand, "Adidas")
        self.assertEqual(p.stock, 10)
        self.assertIsNotNone(p.image_url)

    def test_stock_zero_still_saves(self):
        """Un producto con stock 0 es válido (sin stock pero listable)."""
        p = _make_product(stock=0)
        self.assertEqual(p.stock, 0)


class ChatMessageModelTest(TestCase):
    """Pruebas del modelo ChatMessage."""

    def test_str_truncates_message(self):
        """El __str__ trunca el mensaje a 50 caracteres."""
        msg = ChatMessage.objects.create(
            session_id="sess-1", role="user",
            message="Este es un mensaje muy largo que supera cincuenta caracteres."
        )
        self.assertIn("sess-1", str(msg))

    def test_ordering_by_timestamp(self):
        """Los mensajes deben estar ordenados por timestamp ascendente."""
        sid = str(uuid.uuid4())
        ChatMessage.objects.create(session_id=sid, role="user", message="Primero")
        ChatMessage.objects.create(session_id=sid, role="assistant", message="Segundo")
        msgs = list(ChatMessage.objects.filter(session_id=sid))
        self.assertEqual(msgs[0].message, "Primero")
        self.assertEqual(msgs[1].message, "Segundo")


# ---------------------------------------------------------------------------
# Serializadores
# ---------------------------------------------------------------------------

class ProductSerializerTest(TestCase):
    """Pruebas del serializador ProductSerializer."""

    def test_serializes_all_fields(self):
        """El serializador incluye todos los campos esperados."""
        p = _make_product()
        data = ProductSerializer(p).data
        for field in ['id', 'name', 'brand', 'category', 'size', 'color', 'price', 'stock', 'description', 'image_url']:
            self.assertIn(field, data)

    def test_price_as_string(self):
        """El precio se serializa como string decimal."""
        p = _make_product(price="99.99")
        data = ProductSerializer(p).data
        self.assertEqual(data['price'], '99.99')


class ChatRequestSerializerTest(TestCase):
    """Pruebas del serializador ChatRequestSerializer."""

    def test_valid_data(self):
        """Un mensaje válido pasa la validación."""
        s = ChatRequestSerializer(data={"message": "Hola", "session_id": "abc"})
        self.assertTrue(s.is_valid())

    def test_missing_message_invalid(self):
        """Un mensaje vacío falla la validación."""
        s = ChatRequestSerializer(data={"session_id": "abc"})
        self.assertFalse(s.is_valid())
        self.assertIn('message', s.errors)

    def test_session_id_optional(self):
        """El session_id es opcional."""
        s = ChatRequestSerializer(data={"message": "Hola"})
        self.assertTrue(s.is_valid())


# ---------------------------------------------------------------------------
# Vistas HTML
# ---------------------------------------------------------------------------

class ProductListViewTest(TestCase):
    """Pruebas de la vista principal del catálogo (HTML)."""

    def setUp(self):
        self.client = Client()
        _make_product()

    def test_home_returns_200(self):
        """La vista raíz devuelve HTTP 200."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_context_has_products(self):
        """El contexto de la vista incluye la lista de productos."""
        response = self.client.get('/')
        self.assertIn('products', response.context)
        self.assertGreater(len(response.context['products']), 0)

    def test_session_id_created(self):
        """Se crea un session_id automáticamente en la sesión."""
        response = self.client.get('/')
        self.assertIn('chat_session_id', self.client.session)

    def test_uses_correct_template(self):
        """La vista usa la plantilla correcta."""
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'catalog/index.html')


class ChatViewTest(TestCase):
    """Pruebas de la vista chat_api (HTML/AJAX)."""

    def setUp(self):
        self.client = Client()
        _make_product()

    @patch('catalog.views.GeminiService')
    def test_chat_returns_json(self, mock_ai_cls):
        """POST /chat-api/ retorna JSON con assistant_message."""
        mock_ai = MagicMock()
        mock_ai.generate_response.return_value = "Tenemos Nike Air Max."
        mock_ai_cls.return_value = mock_ai

        response = self.client.post(
            '/chat-api/',
            data=json.dumps({"message": "Qué tienen?", "session_id": "test-123"}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('assistant_message', data)

    def test_chat_empty_message_returns_400(self):
        """POST con mensaje vacío retorna 400."""
        response = self.client.post(
            '/chat-api/',
            data=json.dumps({"message": "", "session_id": "test-123"}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_chat_get_not_allowed(self):
        """GET /chat-api/ retorna 405 Método no permitido."""
        response = self.client.get('/chat-api/')
        self.assertEqual(response.status_code, 405)


# ---------------------------------------------------------------------------
# API REST
# ---------------------------------------------------------------------------

class ProductAPITest(TestCase):
    """Pruebas del endpoint REST GET /api/products/."""

    def setUp(self):
        self.client = APIClient()
        self.p1 = _make_product(name="Air Max 90", brand="Nike")
        self.p2 = _make_product(name="Ultraboost", brand="Adidas", stock=3)

    def test_list_returns_200(self):
        """GET /api/products/ retorna HTTP 200."""
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, 200)

    def test_list_returns_all_products(self):
        """El endpoint devuelve todos los productos."""
        response = self.client.get('/api/products/')
        self.assertEqual(len(response.data), 2)

    def test_list_response_schema(self):
        """Cada producto tiene los campos esperados."""
        response = self.client.get('/api/products/')
        product = response.data[0]
        for field in ['id', 'name', 'brand', 'price', 'stock']:
            self.assertIn(field, product)

    def test_detail_returns_product(self):
        """GET /api/products/<id>/ retorna el producto correcto."""
        response = self.client.get(f'/api/products/{self.p1.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Air Max 90')

    def test_detail_not_found_returns_404(self):
        """GET /api/products/9999/ retorna 404."""
        response = self.client.get('/api/products/9999/')
        self.assertEqual(response.status_code, 404)


class ChatAPITest(TestCase):
    """Pruebas del endpoint REST POST /api/chat/."""

    def setUp(self):
        self.client = APIClient()
        _make_product()

    @patch('catalog.api_views.GeminiService')
    def test_chat_returns_200(self, mock_ai_cls):
        """POST /api/chat/ con datos válidos retorna 200."""
        mock_ai = MagicMock()
        mock_ai.generate_response.return_value = "Tenemos excelentes opciones."
        mock_ai_cls.return_value = mock_ai

        response = self.client.post(
            '/api/chat/',
            data={"message": "Qué zapatos tienen?", "session_id": "s-1"},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('assistant_message', response.data)
        self.assertIn('session_id', response.data)

    def test_chat_missing_message_returns_400(self):
        """POST sin message retorna 400."""
        response = self.client.post('/api/chat/', data={}, format='json')
        self.assertEqual(response.status_code, 400)

    @patch('catalog.api_views.GeminiService')
    def test_chat_auto_session_id(self, mock_ai_cls):
        """Si no se envía session_id, se genera uno automáticamente."""
        mock_ai = MagicMock()
        mock_ai.generate_response.return_value = "OK"
        mock_ai_cls.return_value = mock_ai

        response = self.client.post(
            '/api/chat/',
            data={"message": "Hola"},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('session_id', response.data)
        self.assertTrue(len(response.data['session_id']) > 0)

    def test_chat_history_returns_messages(self):
        """GET /api/chat/history/<sid>/ retorna los mensajes de la sesión."""
        sid = "hist-session"
        ChatMessage.objects.create(session_id=sid, role="user", message="Hola")
        ChatMessage.objects.create(session_id=sid, role="assistant", message="Hola! ¿En qué te ayudo?")

        response = self.client.get(f'/api/chat/history/{sid}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)


# ---------------------------------------------------------------------------
# Dominio (entidades y contexto)
# ---------------------------------------------------------------------------

class DomainEntityTest(TestCase):
    """Pruebas de las entidades del dominio."""

    def test_product_entity_creation(self):
        """ProductEntity se crea con todos los campos."""
        p = ProductEntity(
            id=1, name="Air Max", brand="Nike", category="Running",
            size="42", color="Negro", price=120.0, stock=5,
            description="Test", image_url="https://img.com/x.jpg",
        )
        self.assertEqual(p.brand, "Nike")
        self.assertEqual(p.price, 120.0)

    def test_chat_context_empty(self):
        """ChatContext con lista vacía formatea string vacío."""
        ctx = ChatContext(messages=[])
        result = ctx.format_for_prompt()
        self.assertIsInstance(result, str)

    def test_chat_context_with_messages(self):
        """ChatContext con mensajes incluye el contenido en el prompt."""
        msg = ChatMessageEntity(
            id=None, session_id="s1", role="user",
            message="Quiero zapatos Nike", timestamp=None,
        )
        ctx = ChatContext(messages=[msg])
        result = ctx.format_for_prompt()
        self.assertIn("Nike", result)

    def test_product_dto(self):
        """ProductDTO se instancia correctamente."""
        dto = ProductDTO(
            id=1, name="Stan Smith", brand="Adidas", category="Casual",
            size="41", color="Blanco", price=90.0, stock=12,
            description="Clásico", image_url=None,
        )
        self.assertEqual(dto.name, "Stan Smith")
