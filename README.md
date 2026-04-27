# Elite Zapatos — E-commerce Django + IA

> Taller 1 — Construcción de Software · Universidad EAFIT

Tienda de zapatos premium con asistente de chat inteligente integrado, construida sobre **Django 6.0.4** con arquitectura limpia (Domain → Application → Infrastructure) y API REST documentada con Swagger.

---

## Características

| Módulo | Descripción |
|--------|-------------|
| **Catálogo** | 10 productos con imágenes, filtros por marca/categoría |
| **Chat IA** | Google Gemini 2.0 Flash con historial de conversación |
| **REST API** | Endpoints DRF en `/api/products/` y `/api/chat/` |
| **Swagger UI** | Documentación interactiva en `/docs/` |
| **Admin** | Panel Django en `/admin/` |

---

## Instalación local

```bash
# 1. Clonar el repositorio
git clone https://github.com/Pacha-e/e-commerce-chat-ai.git
cd e-commerce-chat-ai

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate          # Linux/Mac
venv\Scripts\activate             # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env y agregar tu GEMINI_API_KEY

# 5. Aplicar migraciones y poblar datos
python manage.py migrate
python seed_data.py

# 6. Iniciar servidor
python manage.py runserver
```

Abrir: http://127.0.0.1:8000

---

## Docker

```bash
# Construir y ejecutar
docker-compose up --build

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

La app queda disponible en http://localhost:8000

---

## Endpoints API

| Método | URL | Descripción |
|--------|-----|-------------|
| `GET` | `/api/products/` | Listar todos los productos |
| `GET` | `/api/products/<id>/` | Detalle de un producto |
| `POST` | `/api/chat/` | Enviar mensaje al asistente IA |
| `GET` | `/api/chat/history/<session_id>/` | Historial de chat |
| `GET` | `/docs/` | Swagger UI interactivo |

### Ejemplo: POST `/api/chat/`

```json
// Request
{
  "message": "Tienes Nike para running?",
  "session_id": "mi-sesion-123"
}

// Response
{
  "assistant_message": "¡Claro! Tenemos el Nike Air Zoom Pegasus 40 a $120...",
  "timestamp": "2026-04-26T10:30:00",
  "session_id": "mi-sesion-123"
}
```

---

## Tests

```bash
# Ejecutar tests
pytest

# Con reporte de cobertura
pytest --cov=catalog --cov=core_logic --cov-report=term-missing
```

Cobertura actual: **~80%**

---

## Estructura del proyecto

```
e-commerce-django/
├── catalog/            # App Django: modelos, vistas, API, tests
│   ├── models.py       # Entidades de base de datos
│   ├── views.py        # Vistas HTML
│   ├── api_views.py    # Vistas REST (DRF)
│   ├── serializers.py  # Serializadores DRF
│   ├── repositories.py # Capa de infraestructura
│   ├── ai_service.py   # Integración Gemini
│   └── tests.py        # Tests unitarios e integración
├── core/               # Configuración Django
│   ├── settings.py
│   └── urls.py
├── core_logic/         # Arquitectura limpia
│   ├── domain/         # Entidades y repositorios abstractos
│   └── application/    # Servicios y DTOs
├── templates/
│   └── catalog/
│       └── index.html  # UI con Bootstrap 5
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── seed_data.py        # Script para poblar la BD
```

---

## Admin

- URL: http://127.0.0.1:8000/admin/
- Usuario: `admin`
- Contraseña: `admin123`

---

## Variables de entorno

| Variable | Descripción | Requerida |
|----------|-------------|-----------|
| `GEMINI_API_KEY` | API Key de Google AI Studio | Sí |
| `DJANGO_SECRET_KEY` | Clave secreta de Django | Sí (producción) |
| `DEBUG` | Modo debug (`True`/`False`) | No (default: True) |

---

*Desarrollado por Emmanuel Hernández · Taller 1 · Construcción de Software · EAFIT 2026*
