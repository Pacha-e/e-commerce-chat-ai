from django.db import models


class Product(models.Model):
    """
    Modelo de Django para los productos de la tienda (zapatos).

    Attributes:
        name (str): Nombre comercial del zapato.
        brand (str): Marca (Nike, Adidas, etc).
        category (str): Categoría (Running, Casual, etc).
        size (str): Talla disponible.
        color (str): Color del calzado.
        price (Decimal): Precio unitario.
        stock (int): Cantidad en inventario.
        description (str): Descripción detallada obligatoria por el taller.
    """
    name = models.CharField(max_length=200, verbose_name="Nombre")
    brand = models.CharField(max_length=100, verbose_name="Marca")
    category = models.CharField(max_length=100, verbose_name="Categoría")
    size = models.CharField(max_length=20, verbose_name="Talla")
    color = models.CharField(max_length=50, verbose_name="Color")
    price = models.DecimalField(max_length=10, decimal_places=2, max_digits=10, verbose_name="Precio")
    stock = models.IntegerField(verbose_name="Stock")
    description = models.TextField(verbose_name="Descripción")
    image_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="URL Imagen")

    def __str__(self):
        return f"{self.name} ({self.brand})"

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"


class ChatMessage(models.Model):
    """
    Modelo para almacenar el historial de conversación del chat IA.
    """
    session_id = models.CharField(max_length=100, db_index=True, verbose_name="Sesión ID")
    role = models.CharField(max_length=20, choices=[('user', 'Usuario'), ('assistant', 'Asistente')], verbose_name="Rol")
    message = models.TextField(verbose_name="Mensaje")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Fecha/Hora")

    def __str__(self):
        return f"{self.session_id} - {self.role}: {self.message[:50]}..."

    class Meta:
        verbose_name = "Mensaje de Chat"
        verbose_name_plural = "Mensajes de Chat"
        ordering = ['timestamp']
