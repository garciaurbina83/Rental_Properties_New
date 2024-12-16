# Backend Service

Este directorio contiene el servicio backend de la aplicación de Rental Properties, construido con FastAPI y PostgreSQL.

## Estructura del Proyecto

```
backend/
├── app/                 # Código principal de la aplicación
│   ├── api/            # Endpoints de la API
│   ├── core/           # Configuraciones centrales
│   ├── crud/           # Operaciones de base de datos
│   ├── models/         # Modelos SQLAlchemy
│   └── schemas/        # Esquemas Pydantic
├── alembic/            # Migraciones de base de datos
├── tests/              # Tests unitarios y de integración
└── static/             # Archivos estáticos
```

## Requisitos

- Python 3.9+
- PostgreSQL 15+
- Redis 7+

## Configuración

1. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

4. Ejecutar migraciones:
```bash
alembic upgrade head
```

## Desarrollo

1. Iniciar servidor de desarrollo:
```bash
uvicorn main:app --reload
```

2. Acceder a la documentación:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Tests

Ejecutar tests:
```bash
pytest
```

## Docker

El servicio está containerizado. Para ejecutar con Docker:
```bash
cd ../docker
docker-compose up -d
```
