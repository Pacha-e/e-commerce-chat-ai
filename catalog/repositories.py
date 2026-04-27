from typing import List, Optional
from core_logic.domain.entities import Product as ProductEntity, ChatMessage as ChatMessageEntity
from core_logic.domain.repositories import IProductRepository, IChatRepository
from .models import Product as DjangoProduct, ChatMessage as DjangoChatMessage


class DjangoProductRepository(IProductRepository):
    """
    Implementación del repositorio de productos usando el ORM de Django.
    """

    def _to_entity(self, django_product: DjangoProduct) -> ProductEntity:
        return ProductEntity(
            id=django_product.id,
            name=django_product.name,
            brand=django_product.brand,
            category=django_product.category,
            size=django_product.size,
            color=django_product.color,
            price=float(django_product.price),
            stock=django_product.stock,
            description=django_product.description,
            image_url=django_product.image_url
        )

    def get_all(self) -> List[ProductEntity]:
        products = DjangoProduct.objects.all()
        return [self._to_entity(p) for p in products]

    def get_by_id(self, product_id: int) -> Optional[ProductEntity]:
        try:
            p = DjangoProduct.objects.get(id=product_id)
            return self._to_entity(p)
        except DjangoProduct.DoesNotExist:
            return None

    def get_by_brand(self, brand: str) -> List[ProductEntity]:
        products = DjangoProduct.objects.filter(brand__iexact=brand)
        return [self._to_entity(p) for p in products]

    def get_by_category(self, category: str) -> List[ProductEntity]:
        products = DjangoProduct.objects.filter(category__iexact=category)
        return [self._to_entity(p) for p in products]

    def save(self, product: ProductEntity) -> ProductEntity:
        # Nota: En este taller solo consumimos, pero implementamos para cumplir interfaz
        p, created = DjangoProduct.objects.update_or_create(
            id=product.id,
            defaults={
                "name": product.name,
                "brand": product.brand,
                "category": product.category,
                "size": product.size,
                "color": product.color,
                "price": product.price,
                "stock": product.stock,
                "description": product.description
            }
        )
        return self._to_entity(p)

    def delete(self, product_id: int) -> bool:
        deleted_count, _ = DjangoProduct.objects.filter(id=product_id).delete()
        return deleted_count > 0


class DjangoChatRepository(IChatRepository):
    """
    Implementación del repositorio de chat usando el ORM de Django.
    """

    def _to_entity(self, django_msg: DjangoChatMessage) -> ChatMessageEntity:
        return ChatMessageEntity(
            id=django_msg.id,
            session_id=django_msg.session_id,
            role=django_msg.role,
            message=django_msg.message,
            timestamp=django_msg.timestamp
        )

    def save_message(self, message: ChatMessageEntity) -> ChatMessageEntity:
        django_msg = DjangoChatMessage.objects.create(
            session_id=message.session_id,
            role=message.role,
            message=message.message
        )
        # Actualizamos la entidad con el ID generado y timestamp real
        return self._to_entity(django_msg)

    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessageEntity]:
        messages = DjangoChatMessage.objects.filter(
            session_id=session_id
        ).order_by('-timestamp')[:count]
        # Revertimos el orden para que sea cronológico para la IA
        return [self._to_entity(m) for m in reversed(messages)]

    def get_session_history(self, session_id: str, limit: Optional[int] = None) -> List[ChatMessageEntity]:
        qs = DjangoChatMessage.objects.filter(session_id=session_id).order_by('timestamp')
        if limit:
            qs = qs[:limit]
        return [self._to_entity(m) for m in qs]

    def delete_session_history(self, session_id: str) -> int:
        deleted_count, _ = DjangoChatMessage.objects.filter(session_id=session_id).delete()
        return deleted_count
