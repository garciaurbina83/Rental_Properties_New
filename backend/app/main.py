from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
    get_redoc_html
)
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer

from .core.config import settings
from .routers import property, auth
from .core.database import create_tables
from datetime import datetime

# Crear la aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    # API de Gestión de Propiedades en Alquiler

    Esta API proporciona endpoints para gestionar:
    
    * Propiedades: Registro y gestión de propiedades
    * Inquilinos: Información y gestión de inquilinos
    * Contratos: Contratos de alquiler
    * Pagos: Registro y seguimiento de pagos
    * Mantenimiento: Solicitudes y seguimiento de mantenimiento

    ## Autenticación

    Esta API utiliza autenticación JWT a través de Clerk. Para autenticarte:

    1. Obtén un token JWT desde Clerk
    2. Haz clic en el botón "Authorize" arriba
    3. Ingresa tu token en el formato: `Bearer <tu-token>`
    4. Los endpoints protegidos ahora estarán disponibles

    ## Paginación

    Los endpoints que devuelven listas soportan paginación a través de los parámetros `skip` y `limit`.

    ## Documentación Adicional

    * [Términos de Servicio](https://example.com/terms)
    * [Documentación Externa](https://example.com/docs)
    * [Contacto de Soporte](mailto:support@example.com)
    """,
    version=settings.APP_VERSION,
    terms_of_service="https://example.com/terms/",
    contact={
        "name": "Soporte Técnico",
        "url": "https://example.com/contact",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=None,
    redoc_url=None,
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(
    auth.router,
    prefix=settings.API_V1_STR,
    tags=["auth"],
    responses={401: {"description": "No autorizado"}, 403: {"description": "Permiso denegado"}},
)

app.include_router(
    property.router,
    prefix=settings.API_V1_STR,
    tags=["properties"],
    responses={404: {"description": "Propiedad no encontrada"}},
)

# Esquema de seguridad Bearer
security_scheme = HTTPBearer()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Agregar componentes de seguridad y schemas
    openapi_schema["components"] = {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": """
                Autenticación JWT a través de Clerk.
                
                Para obtener un token:
                1. Regístrate o inicia sesión en Clerk
                2. Obtén tu token JWT
                3. Úsalo en el formato: Bearer <token>
                """
            }
        },
        "schemas": {}  # Los schemas se agregarán automáticamente
    }

    # Aplicar seguridad globalmente
    openapi_schema["security"] = [{"BearerAuth": []}]

    # Personalizar la apariencia
    openapi_schema["info"]["x-logo"] = {
        "url": "/static/logo.svg",
        "backgroundColor": "#FFFFFF",
        "altText": "API Logo"
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
        swagger_favicon_url="/static/favicon.svg",
    )

@app.get("/docs/oauth2-redirect", include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
        redoc_favicon_url="/static/favicon.svg",
        with_google_fonts=False,
    )

@app.get("/", tags=["health"])
async def root():
    """
    Endpoint de salud para verificar que la API está funcionando
    
    Returns:
        dict: Estado actual de la API
    """
    return {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Manejador global de excepciones
    
    Args:
        request: Request actual
        exc: Excepción capturada
    
    Returns:
        JSONResponse: Respuesta de error formateada
    """
    error_response = {
        "detail": str(exc),
        "type": exc.__class__.__name__,
        "path": request.url.path
    }
    
    if hasattr(exc, "status_code"):
        status_code = exc.status_code
    else:
        status_code = 500
        error_response["detail"] = "Internal Server Error"
    
    return JSONResponse(
        status_code=status_code,
        content=error_response
    )

@app.on_event("startup")
async def startup_event():
    """Initialize application resources"""
    create_tables()
