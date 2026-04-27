import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from catalog.models import Product

products = [
    {
        "name": "Air Zoom Pegasus 40",
        "brand": "Nike",
        "category": "Running",
        "size": "42",
        "color": "Negro",
        "price": 120.0,
        "stock": 5,
        "description": "Zapatilla de running con amortiguación Zoom Air. Ideal para carreras de media y larga distancia.",
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80"
    },
    {
        "name": "Ultraboost 22",
        "brand": "Adidas",
        "category": "Running",
        "size": "41",
        "color": "Blanco",
        "price": 150.0,
        "stock": 3,
        "description": "Zapatilla de alto rendimiento con tecnología Boost para máxima devolución de energía.",
        "image_url": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=400&q=80"
    },
    {
        "name": "Suede Classic",
        "brand": "Puma",
        "category": "Casual",
        "size": "40",
        "color": "Azul",
        "price": 80.0,
        "stock": 10,
        "description": "Clásico icónico de Puma en suede. Perfecto para el uso diario con estilo retro.",
        "image_url": "https://images.unsplash.com/photo-1600185365926-3a2ce3cdb9eb?w=400&q=80"
    },
    {
        "name": "Air Force 1 '07",
        "brand": "Nike",
        "category": "Casual",
        "size": "43",
        "color": "Blanco",
        "price": 110.0,
        "stock": 8,
        "description": "El icónico sneaker de Nike. Diseño atemporal con suela Air para comodidad todo el día.",
        "image_url": "https://images.unsplash.com/photo-1597045566677-8cf032ed6634?w=400&q=80"
    },
    {
        "name": "Stan Smith",
        "brand": "Adidas",
        "category": "Casual",
        "size": "42",
        "color": "Blanco/Verde",
        "price": 90.0,
        "stock": 12,
        "description": "Zapatilla clásica de tenis reconvertida en ícono de moda urbana. Cuero premium.",
        "image_url": "https://images.unsplash.com/photo-1539185441755-769473a23570?w=400&q=80"
    },
    {
        "name": "574 Core",
        "brand": "New Balance",
        "category": "Casual",
        "size": "44",
        "color": "Gris",
        "price": 85.0,
        "stock": 7,
        "description": "Zapatilla versátil con tecnología ENCAP para soporte y amortiguación duradera.",
        "image_url": "https://images.unsplash.com/photo-1579338559194-a162d19bf842?w=400&q=80"
    },
    {
        "name": "Classic Leather",
        "brand": "Reebok",
        "category": "Casual",
        "size": "41",
        "color": "Negro",
        "price": 75.0,
        "stock": 6,
        "description": "Zapatilla retro de cuero suave con suela EVA para amortiguación ligera.",
        "image_url": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=400&q=80"
    },
    {
        "name": "Air Max 90",
        "brand": "Nike",
        "category": "Running",
        "size": "42",
        "color": "Rojo/Negro",
        "price": 130.0,
        "stock": 4,
        "description": "Diseño revolucionario con unidad Air Max visible. Comodidad superior y estilo audaz.",
        "image_url": "https://images.unsplash.com/photo-1605348532760-6753d2c43329?w=400&q=80"
    },
    {
        "name": "Oxford Classic",
        "brand": "Clarks",
        "category": "Formal",
        "size": "43",
        "color": "Marrón",
        "price": 160.0,
        "stock": 3,
        "description": "Zapato formal de cuero genuino con suela de goma. Elegante para oficina y eventos.",
        "image_url": "https://images.unsplash.com/photo-1560343090-f0409e92791a?w=400&q=80"
    },
    {
        "name": "RS-X Reinvention",
        "brand": "Puma",
        "category": "Casual",
        "size": "43",
        "color": "Multicolor",
        "price": 95.0,
        "stock": 9,
        "description": "Zapatilla chunky con diseño futurista y tecnología RS para amortiguación de carrera.",
        "image_url": "https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?w=400&q=80"
    }
]

def seed_products():
    for p_data in products:
        obj, created = Product.objects.update_or_create(
            name=p_data["name"],
            brand=p_data["brand"],
            defaults={k: v for k, v in p_data.items() if k not in ("name", "brand")}
        )
        action = "Creado" if created else "Actualizado"
        print(f"{action}: {obj.brand} {obj.name}")
    print(f"[OK] Se procesaron {len(products)} productos correctamente.")

if __name__ == "__main__":
    seed_products()
