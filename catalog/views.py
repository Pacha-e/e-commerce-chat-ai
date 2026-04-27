import json
import uuid
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from core_logic.application.product_service import ProductService
from core_logic.application.chat_service import ChatService
from core_logic.application.dtos import ChatMessageRequestDTO
from .repositories import DjangoProductRepository, DjangoChatRepository
from .ai_service import GeminiService


def get_services():
    """Helper para instanciar los servicios con persistencia Django."""
    product_repo = DjangoProductRepository()
    chat_repo = DjangoChatRepository()
    ai_service = GeminiService()
    
    product_service = ProductService(product_repo)
    chat_service = ChatService(product_repo, chat_repo, ai_service)
    
    return product_service, chat_service


def product_list(request):
    """Vista principal: Muestra el catálogo de productos."""
    product_service, _ = get_services()
    products = product_service.get_all_products()
    
    # Generamos un session_id si no existe uno en la sesión de Django
    if 'chat_session_id' not in request.session:
        request.session['chat_session_id'] = str(uuid.uuid4())
        
    return render(request, 'catalog/index.html', {
        'products': products,
        'session_id': request.session['chat_session_id']
    })


@csrf_exempt
def chat_api(request):
    """API endpoint para el chat (AJAX)."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message')
            session_id = data.get('session_id') or request.session.get('chat_session_id')
            
            if not message:
                return JsonResponse({'error': 'Mensaje vacío'}, status=400)
            
            _, chat_service = get_services()
            request_dto = ChatMessageRequestDTO(session_id=session_id, message=message)
            response = chat_service.process_message(request_dto)
            
            return JsonResponse({
                'assistant_message': response.assistant_message,
                'timestamp': response.timestamp.isoformat()
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Método no permitido'}, status=405)


def chat_history(request, session_id):
    """Obtiene el historial de chat para cargar en la UI."""
    _, chat_service = get_services()
    history = chat_service.get_session_history(session_id)
    
    return JsonResponse([
        {
            'role': msg.role,
            'message': msg.message,
            'timestamp': msg.timestamp.isoformat()
        } for msg in history
    ], safe=False)
