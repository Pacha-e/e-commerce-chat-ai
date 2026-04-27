"""
DTOs (Data Transfer Objects) para la transferencia de datos entre capas.

Define los esquemas de validación con Pydantic para garantizar que los datos
que entran y salen de la API cumplen con el formato esperado. Los DTOs actúan
como contratos entre la capa de presentación y la capa de aplicación.
"""
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class ProductDTO(BaseModel):
    """
    DTO para transferir datos de productos entre capas.

    Pydantic valida automáticamente los tipos y restricciones definidas.
    Permite crear instancias desde modelos ORM gracias a from_attributes.

    Attributes:
        id (Optional[int]): ID del producto (None para nuevos productos).
        name (str): Nombre del producto.
        brand (str): Marca del producto.
        category (str): Categoría del producto.
        size (str): Talla del zapato.
        color (str): Color del producto.
        price (float): Precio en dólares (debe ser > 0).
        stock (int): Cantidad en inventario (debe ser >= 0).
        description (str): Descripción del producto.
    """
    id: Optional[int] = None
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str
    image_url: Optional[str] = None

    @field_validator('price')
    @classmethod
    def price_must_be_positive(cls, v):
        """
        Valida que el precio sea mayor a 0.

        Args:
            v (float): Valor del precio a validar.

        Returns:
            float: Precio validado.

        Raises:
            ValueError: Si el precio es menor o igual a 0.
        """
        if v <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        return v

    @field_validator('stock')
    @classmethod
    def stock_must_be_non_negative(cls, v):
        """
        Valida que el stock no sea negativo.

        Args:
            v (int): Valor del stock a validar.

        Returns:
            int: Stock validado.

        Raises:
            ValueError: Si el stock es negativo.
        """
        if v < 0:
            raise ValueError("El stock no puede ser negativo")
        return v

    model_config = {"from_attributes": True}


class ChatMessageRequestDTO(BaseModel):
    """
    DTO para recibir mensajes del usuario en el endpoint /chat.

    Valida que el mensaje y el session_id no estén vacíos.

    Attributes:
        session_id (str): Identificador único de la sesión del usuario.
        message (str): Contenido del mensaje del usuario.

    Example:
        >>> request = ChatMessageRequestDTO(
        ...     session_id="user123",
        ...     message="Busco zapatos Nike para correr"
        ... )
    """
    session_id: str
    message: str

    @field_validator('message')
    @classmethod
    def message_not_empty(cls, v):
        """
        Valida que el mensaje no esté vacío ni contenga solo espacios.

        Args:
            v (str): Contenido del mensaje.

        Returns:
            str: Mensaje validado (sin espacios extra).

        Raises:
            ValueError: Si el mensaje está vacío.
        """
        if not v or not v.strip():
            raise ValueError("El mensaje no puede estar vacío")
        return v.strip()

    @field_validator('session_id')
    @classmethod
    def session_id_not_empty(cls, v):
        """
        Valida que el session_id no esté vacío.

        Args:
            v (str): Identificador de sesión.

        Returns:
            str: Session ID validado.

        Raises:
            ValueError: Si el session_id está vacío.
        """
        if not v or not v.strip():
            raise ValueError("El session_id no puede estar vacío")
        return v.strip()


class ChatMessageResponseDTO(BaseModel):
    """
    DTO para enviar la respuesta del chat al cliente.

    Contiene el mensaje original del usuario, la respuesta generada
    por la IA y la marca de tiempo de la interacción.

    Attributes:
        session_id (str): Identificador de la sesión.
        user_message (str): Mensaje original del usuario.
        assistant_message (str): Respuesta generada por la IA.
        timestamp (datetime): Momento de la interacción.
    """
    session_id: str
    user_message: str
    assistant_message: str
    timestamp: datetime


class ChatHistoryDTO(BaseModel):
    """
    DTO para mostrar un mensaje individual del historial de chat.

    Attributes:
        id (int): ID del mensaje.
        role (str): Rol del emisor ('user' o 'assistant').
        message (str): Contenido del mensaje.
        timestamp (datetime): Momento del mensaje.
    """
    id: int
    role: str
    message: str
    timestamp: datetime

    model_config = {"from_attributes": True}
