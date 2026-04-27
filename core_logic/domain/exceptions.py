"""
Excepciones específicas del dominio.

Define excepciones personalizadas que representan errores de negocio,
no errores técnicos. Esto permite un manejo de errores más descriptivo
y específico en todas las capas de la aplicación.
"""


class ProductNotFoundError(Exception):
    """
    Excepción que se lanza cuando se busca un producto que no existe.

    Attributes:
        product_id (int): ID del producto que no fue encontrado.
        message (str): Mensaje descriptivo del error.

    Example:
        >>> raise ProductNotFoundError(42)
        ProductNotFoundError: Producto con ID 42 no encontrado
    """

    def __init__(self, product_id: int = None):
        """
        Inicializa la excepción con un ID de producto opcional.

        Args:
            product_id (int, optional): ID del producto no encontrado.
                Si se proporciona, el mensaje incluirá el ID.
        """
        if product_id is not None:
            self.message = f"Producto con ID {product_id} no encontrado"
        else:
            self.message = "Producto no encontrado"
        self.product_id = product_id
        super().__init__(self.message)


class InvalidProductDataError(Exception):
    """
    Excepción que se lanza cuando los datos de un producto son inválidos.

    Se utiliza cuando los datos proporcionados para crear o actualizar
    un producto no cumplen con las reglas de negocio.

    Attributes:
        message (str): Descripción del error de validación.

    Example:
        >>> raise InvalidProductDataError("El precio debe ser mayor a 0")
        InvalidProductDataError: El precio debe ser mayor a 0
    """

    def __init__(self, message: str = "Datos de producto inválidos"):
        """
        Inicializa la excepción con un mensaje personalizado.

        Args:
            message (str): Descripción del error. Por defecto: 'Datos de producto inválidos'.
        """
        self.message = message
        super().__init__(self.message)


class ChatServiceError(Exception):
    """
    Excepción que se lanza cuando hay un error en el servicio de chat.

    Encapsula errores de comunicación con la IA, problemas de formato
    de prompt, o cualquier fallo en el procesamiento del chat.

    Attributes:
        message (str): Descripción del error en el servicio de chat.

    Example:
        >>> raise ChatServiceError("Error al comunicarse con Gemini API")
        ChatServiceError: Error al comunicarse con Gemini API
    """

    def __init__(self, message: str = "Error en el servicio de chat"):
        """
        Inicializa la excepción con un mensaje personalizado.

        Args:
            message (str): Descripción del error. Por defecto: 'Error en el servicio de chat'.
        """
        self.message = message
        super().__init__(self.message)
