from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # Vistas HTML (UI)
    path('', views.product_list, name='product_list'),
    path('chat-api/', views.chat_api, name='chat_api'),
    path('chat-history/<str:session_id>/', views.chat_history, name='chat_history'),

    # REST API (Swagger)
    path('api/products/', api_views.ProductListAPIView.as_view(), name='api_product_list'),
    path('api/products/<int:pk>/', api_views.ProductDetailAPIView.as_view(), name='api_product_detail'),
    path('api/chat/', api_views.ChatAPIView.as_view(), name='api_chat'),
    path('api/chat/history/<str:session_id>/', api_views.ChatHistoryAPIView.as_view(), name='api_chat_history'),
]
