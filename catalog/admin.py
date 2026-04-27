from django.contrib import admin
from .models import Product, ChatMessage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'price', 'stock', 'category')
    list_filter = ('brand', 'category')
    search_fields = ('name', 'brand', 'description')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'role', 'timestamp', 'message_excerpt')
    list_filter = ('role', 'timestamp')
    search_fields = ('session_id', 'message')

    def message_excerpt(self, obj):
        return obj.message[:50]
    message_excerpt.short_description = "Contenido"
