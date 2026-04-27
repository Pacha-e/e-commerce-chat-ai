"""
Interfaces de repositorio del dominio.

Define los contratos (interfaces abstractas) que especifican CÓMO se accede
a los datos, sin implementar el acceso real. Las implementaciones concretas
se encuentran en la capa de infraestructura.

Esto permite que el dominio sea completamente independiente de la base de datos
utilizada (SQLite, PostgreSQL, MongoDB, etc.).
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Product, ChatMessage


class IProductRepository(ABC):
    """
    Interface que define el contrato para acceder a productos.

    Las implementaciones concretas de esta interface se encuentran en la capa
    de infraestructura (por ejemplo, SQLProductRepository).

    Todas las operaciones son síncronas para compatibilidad con SQLAlchemy
    y SQLite.
    """

    @abstractmethod
    def get_all(self) -> List[Product]:
        """
        Obtiene todos los productos registrados en el sistema.

        Returns:
            List[Product]: Lista completa de productos.
        """
        pass

    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        Obtiene un producto específico por su identificador.

        Args:
            product_id (int): ID del producto a buscar.

        Returns:
            Optional[Product]: El producto encontrado o None si no existe.
        """
        pass

    @abstractmethod
    def get_by_brand(self, brand: str) -> List[Product]:
        """
        Obtiene todos los productos de una marca específica.

        Args:
            brand (str): Nombre de la marca (ej: 'Nike', 'Adidas').

        Returns:
            List[Product]: Lista de productos de la marca indicada.
        """
        pass

    @abstractmethod
    def get_by_category(self, category: str) -> List[Product]:
        """
        Obtiene todos los productos de una categoría específica.

        Args:
            category (str): Nombre de la categoría (ej: 'Running', 'Casual').

        Returns:
            List[Product]: Lista de productos de la categoría indicada.
        """
        pass

    @abstractmethod
    def save(self, product: Product) -> Product:
        """
        Guarda o actualiza un producto en el sistema.

        Si el producto tiene ID, se actualiza. Si no tiene ID (None),
        se crea uno nuevo con ID auto-generado.

        Args:
            product (Product): Entidad de producto a guardar.

        Returns:
            Product: El producto guardado con su ID asignado.
        """
        pass

    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """
        Elimina un producto del sistema por su ID.

        Args:
            product_id (int): ID del producto a eliminar.

        Returns:
            bool: True si se eliminó exitosamente, False si no existía.
        """
        pass


class IChatRepository(ABC):
    """
    Interface para gestionar el historial de conversaciones del chat.

    Define las operaciones necesarias para persistir y recuperar mensajes
    del chat, manteniendo el historial conversacional por sesión.
    """

    @abstractmethod
    def save_message(self, message: ChatMessage) -> ChatMessage:
        """
        Guarda un mensaje en el historial de la conversación.

        Args:
            message (ChatMessage): Mensaje a guardar.

        Returns:
            ChatMessage: El mensaje guardado con su ID asignado.
        """
        pass

    @abstractmethod
    def get_session_history(self, session_id: str, limit: Optional[int] = None) -> List[ChatMessage]:
        """
        Obtiene el historial completo de una sesión de chat.

        Args:
            session_id (str): Identificador de la sesión.
            limit (Optional[int]): Límite de mensajes a retornar.
                Si es None, retorna todos los mensajes.

        Returns:
            List[ChatMessage]: Mensajes en orden cronológico (más antiguos primero).
        """
        pass

    @abstractmethod
    def delete_session_history(self, session_id: str) -> int:
        """
        Elimina todo el historial de una sesión de chat.

        Args:
            session_id (str): Identificador de la sesión a limpiar.

        Returns:
            int: Cantidad de mensajes eliminados.
        """
        pass

    @abstractmethod
    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        """
        Obtiene los últimos N mensajes de una sesión.

        Es crucial para mantener el contexto conversacional con la IA.
        Los mensajes se retornan en orden cronológico (más antiguos primero).

        Args:
            session_id (str): Identificador de la sesión.
            count (int): Cantidad de mensajes recientes a obtener.

        Returns:
            List[ChatMessage]: Últimos N mensajes en orden cronológico.
        """
        pass
