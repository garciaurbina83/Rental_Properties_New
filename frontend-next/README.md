# Rental Properties Management System

Sistema integral para la gestión y administración de propiedades de renta.

## Tecnologías Principales

- **Backend:** Python (FastAPI)
- **Frontend Web:** React
- **Frontend Mobile:** React Native
- **Base de datos:** PostgreSQL
- **Autenticación:** Clerk
- **Documentación:** Swagger UI y ReDoc

## Documentación

- [API Documentation](docs/api.md) - Documentación detallada de los endpoints de la API
- Swagger UI (disponible en `/docs` cuando el servidor está corriendo)
- ReDoc (disponible en `/redoc` cuando el servidor está corriendo)

## Estructura del Proyecto

```
rental-properties/
├── backend/           # Servidor FastAPI
│   ├── app/          # Código principal
│   │   ├── core/     # Configuración y utilidades
│   │   ├── routers/  # Endpoints de la API
│   │   ├── schemas/  # Modelos Pydantic
│   │   └── static/   # Archivos estáticos
├── frontend/         # Aplicación web React
├── mobile/          # Aplicación móvil React Native
└── docs/            # Documentación
```

## Requisitos Previos

- Python 3.8+
- Node.js 16+
- PostgreSQL 13+
- npm o yarn
- Cuenta en Clerk (para autenticación)

## Configuración del Entorno

1. Clonar el repositorio
```bash
git clone [url-del-repositorio]
```

2. Configurar el backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configurar variables de entorno
Crear un archivo `.env` en la carpeta `backend` con:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
CLERK_SECRET_KEY=your_clerk_secret_key
CLERK_FRONTEND_API=your_clerk_frontend_api
ENVIRONMENT=development
CORS_ORIGINS=["http://localhost:3000"]
```

4. Configurar el frontend
```bash
cd frontend
npm install
```

## Características Principales

### Backend (FastAPI)
- **Autenticación JWT** con Clerk
- **RBAC (Control de Acceso Basado en Roles)**:
  - Admin
  - Property Manager
  - Tenant
  - Maintenance Staff
  - Viewer
- **API RESTful** con endpoints para:
  - Gestión de propiedades
  - Administración de inquilinos
  - Contratos de alquiler
  - Sistema de pagos
  - Tickets de mantenimiento
- **Documentación Interactiva**:
  - Swagger UI: `/docs`
  - ReDoc: `/redoc`

### Seguridad
- Autenticación JWT con Clerk
- Protección CORS configurada
- Validación de tokens y permisos
- Manejo seguro de errores
- Logs de auditoría

## Desarrollo

1. Iniciar el backend:
```bash
cd backend
uvicorn app.main:app --reload
```

2. Acceder a la documentación:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Autenticación

1. Registrarse en [Clerk](https://clerk.dev)
2. Obtener un token JWT
3. Usar el token en las peticiones:
   ```bash
   curl -H "Authorization: Bearer <tu-token>" http://localhost:8000/api/v1/properties
   ```

## Endpoints Principales

- `GET /api/v1/properties`: Listar propiedades
- `POST /api/v1/properties`: Crear propiedad
- `GET /api/v1/tenants`: Listar inquilinos
- `POST /api/v1/contracts`: Crear contrato
- `GET /api/v1/payments`: Listar pagos
- `POST /api/v1/maintenance`: Crear ticket de mantenimiento

## Contribución

1. Fork el repositorio
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.
