"""
Servicio de aplicación para la gestión de productos.

Implementa los casos de uso relacionados con productos, orquestando
la interacción entre el repositorio de productos y las entidades
del dominio. Actúa como intermediario entre la API y el dominio.
"""
from typing import List, Optional
from core_logic.domain.repositories import IProductRepository
from core_logic.domain.entities import Product
from core_logic.domain.exceptions import ProductNotFoundError, InvalidProductDataError
from core_logic.application.dtos import ProductDTO


class ProductService:
    """
    Servicio para gestionar operaciones de productos.

    Orquesta los casos de uso de productos utilizando el repositorio
    inyectado. Convierte entre DTOs y entidades del dominio.

    Attributes:
        repository (IProductRepository): Repositorio de productos inyectado.

    Example:
        >>> service = ProductService(product_repository)
        >>> productos = service.get_all_products()
        >>> producto = service.get_product_by_id(1)
    """

    def __init__(self, repository: IProductRepository):
        """
        Inicializa el servicio con un repositorio de productos.

        Args:
            repository (IProductRepository): Implementación del repositorio
                de productos a usar (inyección de dependencias).
        """
        self.repository = repository

    def get_all_products(self) -> List[ProductDTO]:
        """
        Obtiene todos los productos registrados en el sistema.

        Returns:
            List[ProductDTO]: Lista de DTOs con la información de todos los productos.
        """
        products = self.repository.get_all()
        return [self._entity_to_dto(p) for p in products]

    def get_product_by_id(self, product_id: int) -> ProductDTO:
        """
        Obtiene un producto específico por su ID.

        Args:
            product_id (int): ID del producto a buscar.

        Returns:
            ProductDTO: DTO con la información del producto.

        Raises:
            ProductNotFoundError: Si no existe un producto con el ID indicado.
        """
        product = self.repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(product_id)
        return self._entity_to_dto(product)

    def search_products(self, brand: Optional[str] = None, category: Optional[str] = None) -> List[ProductDTO]:
        """
        Busca productos por marca y/o categoría.

        Args:
            brand (Optional[str]): Filtrar por marca.
            category (Optional[str]): Filtrar por categoría.

        Returns:
            List[ProductDTO]: Productos que coinciden con los filtros.
        """
        if brand:
            products = self.repository.get_by_brand(brand)
        elif category:
            products = self.repository.get_by_category(category)
        else:
            products = self.repository.get_all()
        return [self._entity_to_dto(p) for p in products]

    def create_product(self, product_dto: ProductDTO) -> ProductDTO:
        """
        Crea un nuevo producto en el sistema.

        Args:
            product_dto (ProductDTO): Datos del producto a crear.

        Returns:
            ProductDTO: Producto creado con ID asignado.

        Raises:
            InvalidProductDataError: Si los datos del producto son inválidos.
        """
        try:
            product = Product(
                id=None,
                name=product_dto.name,
                brand=product_dto.brand,
                category=product_dto.category,
                size=product_dto.size,
                color=product_dto.color,
                price=product_dto.price,
                stock=product_dto.stock,
                description=product_dto.description
            )
        except ValueError as e:
            raise InvalidProductDataError(str(e))

        saved = self.repository.save(product)
        return self._entity_to_dto(saved)

    def update_product(self, product_id: int, product_dto: ProductDTO) -> ProductDTO:
        """
        Actualiza un producto existente.

        Args:
            product_id (int): ID del producto a actualizar.
            product_dto (ProductDTO): Nuevos datos del producto.

        Returns:
            ProductDTO: Producto actualizado.

        Raises:
            ProductNotFoundError: Si el producto no existe.
            InvalidProductDataError: Si los datos son inválidos.
        """
        existing = self.repository.get_by_id(product_id)
        if existing is None:
            raise ProductNotFoundError(product_id)

        try:
            updated = Product(
                id=product_id,
                name=product_dto.name,
                brand=product_dto.brand,
                category=product_dto.category,
                size=product_dto.size,
                color=product_dto.color,
                price=product_dto.price,
                stock=product_dto.stock,
                description=product_dto.description
            )
        except ValueError as e:
            raise InvalidProductDataError(str(e))

        saved = self.repository.save(updated)
        return self._entity_to_dto(saved)

    def delete_product(self, product_id: int) -> bool:
        """
        Elimina un producto del sistema.

        Args:
            product_id (int): ID del producto a eliminar.

        Returns:
            bool: True si se eliminó exitosamente.

        Raises:
            ProductNotFoundError: Si el producto no existe.
        """
        existing = self.repository.get_by_id(product_id)
        if existing is None:
            raise ProductNotFoundError(product_id)
        return self.repository.delete(product_id)

    def get_available_products(self) -> List[ProductDTO]:
        """
        Obtiene solo los productos con stock disponible (stock > 0).

        Returns:
            List[ProductDTO]: Productos disponibles para la venta.
        """
        products = self.repository.get_all()
        available = [p for p in products if p.is_available()]
        return [self._entity_to_dto(p) for p in available]

    @staticmethod
    def _entity_to_dto(product: Product) -> ProductDTO:
        """
        Convierte una entidad Product del dominio a un ProductDTO.

        Args:
            product (Product): Entidad de dominio.

        Returns:
            ProductDTO: DTO con los datos del producto.
        """
        return ProductDTO(
            id=product.id,
            name=product.name,
            brand=product.brand,
            category=product.category,
            size=product.size,
            color=product.color,
            price=product.price,
            stock=product.stock,
            description=product.description,
            image_url=product.image_url
        )
