"""
Entidades del dominio del e-commerce con chat IA.

Este módulo define las entidades principales del negocio:
- Product: Representa un zapato en el inventario.
- ChatMessage: Representa un mensaje en la conversación.
- ChatContext: Encapsula el contexto conversacional para la IA.

Estas entidades contienen la lógica de negocio pura y no dependen
de ningún framework, base de datos o servicio externo.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Product:
    """
    Entidad que representa un producto (zapato) en el e-commerce.

    Esta clase encapsula la lógica de negocio relacionada con productos,
    incluyendo validaciones de precio, stock y disponibilidad.

    Attributes:
        id (Optional[int]): Identificador único del producto.
        name (str): Nombre del producto.
        brand (str): Marca del producto (Nike, Adidas, Puma, etc.).
        category (str): Categoría del producto (Running, Casual, Formal).
        size (str): Talla del zapato.
        color (str): Color del producto.
        price (float): Precio en dólares. Debe ser mayor a 0.
        stock (int): Cantidad disponible en inventario. No puede ser negativo.
        description (str): Descripción detallada del producto.

    Example:
        >>> producto = Product(
        ...     id=None, name="Air Zoom Pegasus", brand="Nike",
        ...     category="Running", size="42", color="Negro",
        ...     price=120.0, stock=5, description="Zapato para correr"
        ... )
        >>> producto.is_available()
        True
    """
    id: Optional[int]
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str
    image_url: Optional[str] = None

    def __post_init__(self):
        """
        Validaciones que se ejecutan automáticamente después de crear el objeto.

        Verifica las reglas de negocio invariantes del producto:
        - El precio debe ser mayor a 0.
        - El stock no puede ser negativo.
        - El nombre no puede estar vacío.

        Raises:
            ValueError: Si el precio no es mayor a 0.
            ValueError: Si el stock es negativo.
            ValueError: Si el nombre está vacío.
        """
        if self.price <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        if self.stock < 0:
            raise ValueError("El stock no puede ser negativo")
        if not self.name or not self.name.strip():
            raise ValueError("El nombre no puede estar vacío")

    def is_available(self) -> bool:
        """
        Verifica si el producto tiene stock disponible para la venta.

        Returns:
            bool: True si el stock es mayor a 0, False en caso contrario.

        Example:
            >>> producto = Product(id=1, name="Nike", brand="Nike",
            ...     category="Running", size="42", color="Negro",
            ...     price=100.0, stock=5, description="Zapato")
            >>> producto.is_available()
            True
        """
        return self.stock > 0

    def reduce_stock(self, quantity: int) -> None:
        """
        Reduce el stock del producto en la cantidad especificada.

        Se utiliza típicamente cuando se realiza una venta.
        Valida que haya suficiente stock antes de reducir.

        Args:
            quantity (int): Cantidad a reducir del stock. Debe ser positivo.

        Raises:
            ValueError: Si quantity es menor o igual a 0.
            ValueError: Si quantity es mayor al stock disponible.

        Example:
            >>> producto = Product(id=1, name="Nike", brand="Nike",
            ...     category="Running", size="42", color="Negro",
            ...     price=100.0, stock=5, description="Zapato")
            >>> producto.reduce_stock(2)
            >>> print(producto.stock)
            3
        """
        if quantity <= 0:
            raise ValueError("La cantidad a reducir debe ser positiva")
        if quantity > self.stock:
            raise ValueError(
                f"Stock insuficiente. Disponible: {self.stock}, solicitado: {quantity}"
            )
        self.stock -= quantity

    def increase_stock(self, quantity: int) -> None:
        """
        Aumenta el stock del producto en la cantidad especificada.

        Se utiliza para reabastecimiento o devoluciones.

        Args:
            quantity (int): Cantidad a agregar al stock. Debe ser positivo.

        Raises:
            ValueError: Si quantity es menor o igual a 0.
        """
        if quantity <= 0:
            raise ValueError("La cantidad a agregar debe ser positiva")
        self.stock += quantity


@dataclass
class ChatMessage:
    """
    Entidad que representa un mensaje en la conversación del chat.

    Cada mensaje pertenece a una sesión identificada por session_id,
    y puede ser enviado por el usuario ('user') o por el asistente ('assistant').

    Attributes:
        id (Optional[int]): Identificador único del mensaje.
        session_id (str): Identificador de la sesión del usuario.
        role (str): Rol del emisor, debe ser 'user' o 'assistant'.
        message (str): Contenido textual del mensaje.
        timestamp (datetime): Momento en que se envió el mensaje.

    Example:
        >>> from datetime import datetime
        >>> msg = ChatMessage(
        ...     id=None, session_id="user123", role="user",
        ...     message="Hola, busco zapatos", timestamp=datetime.utcnow()
        ... )
        >>> msg.is_from_user()
        True
    """
    id: Optional[int]
    session_id: str
    role: str
    message: str
    timestamp: datetime

    def __post_init__(self):
        """
        Validaciones posteriores a la creación del objeto.

        Raises:
            ValueError: Si el role no es 'user' ni 'assistant'.
            ValueError: Si el mensaje está vacío.
            ValueError: Si el session_id está vacío.
        """
        if self.role not in ("user", "assistant"):
            raise ValueError(
                f"El rol debe ser 'user' o 'assistant', se recibió: '{self.role}'"
            )
        if not self.message or not self.message.strip():
            raise ValueError("El mensaje no puede estar vacío")
        if not self.session_id or not self.session_id.strip():
            raise ValueError("El session_id no puede estar vacío")

    def is_from_user(self) -> bool:
        """
        Verifica si el mensaje fue enviado por el usuario.

        Returns:
            bool: True si el rol es 'user'.
        """
        return self.role == "user"

    def is_from_assistant(self) -> bool:
        """
        Verifica si el mensaje fue enviado por el asistente de IA.

        Returns:
            bool: True si el rol es 'assistant'.
        """
        return self.role == "assistant"


@dataclass
class ChatContext:
    """
    Value Object que encapsula el contexto conversacional.

    Mantiene los mensajes recientes de una conversación para proporcionar
    memoria a la IA durante la generación de respuestas. Limita la cantidad
    de mensajes a max_messages para controlar el tamaño del prompt.

    Attributes:
        messages (list[ChatMessage]): Lista de mensajes de la conversación.
        max_messages (int): Número máximo de mensajes a mantener (default: 6).

    Example:
        >>> contexto = ChatContext(messages=[msg1, msg2, msg3])
        >>> contexto.format_for_prompt()
        'Usuario: Hola\\nAsistente: ¡Hola! ¿En qué puedo ayudarte?'
    """
    messages: list
    max_messages: int = 6

    def get_recent_messages(self) -> list:
        """
        Obtiene los últimos N mensajes según max_messages.

        Utiliza slicing de Python para obtener los mensajes más recientes
        de la conversación.

        Returns:
            list[ChatMessage]: Los mensajes más recientes, hasta max_messages.
        """
        return self.messages[-self.max_messages:]

    def format_for_prompt(self) -> str:
        """
        Formatea los mensajes recientes para incluirlos en el prompt de la IA.

        Genera un string con el historial de la conversación en formato legible:
            Usuario: mensaje del usuario
            Asistente: respuesta del asistente

        Returns:
            str: Historial formateado como texto plano.
                 Retorna '[Sin historial previo]' si no hay mensajes.
        """
        if not self.messages:
            return "[Sin historial previo]"

        lines = []
        for msg in self.get_recent_messages():
            role_label = "Usuario" if msg.is_from_user() else "Asistente"
            lines.append(f"{role_label}: {msg.message}")
        return "\n".join(lines)
