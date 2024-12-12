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
from dotenv import load_dotenv
import os

from .core.config import settings
from .api.v1.api import api_router
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

# Crear la aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="""
    # API de Gestión de Propiedades en Alquiler

    Esta API proporciona endpoints para gestionar propiedades en alquiler, incluyendo:
    
    * Gestión de propiedades
    * Gestión de inquilinos
    * Gestión de contratos
    * Gestión de pagos
    * Reportes y análisis
    
    ## Características principales
    
    * Documentación interactiva
    * Validación de datos
    * Manejo de errores consistente
    * Paginación y filtrado
    * Monitoreo y logging
    
    ## Tecnologías utilizadas
    
    * FastAPI
    * PostgreSQL
    * SQLAlchemy
    * Pydantic
    * Redis
    * Alembic
    * OpenAPI (Swagger)
    """,
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
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar CORS
origins = [
    "http://localhost:3000",  # Frontend Next.js
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Incluir todas las rutas bajo el prefijo /api/v1
app.include_router(api_router, prefix=settings.API_V1_STR)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
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

@app.get("/")
async def root():
    """
    Endpoint de salud para verificar que la API está funcionando
    
    Returns:
        dict: Estado actual de la API
    """
    return {
        "status": "ok",
        "message": "API is running",
        "timestamp": datetime.now().isoformat(),
        "version": app.version
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

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
        "status": "error",
        "message": str(exc),
        "type": exc.__class__.__name__,
        "path": request.url.path
    }
    
    if hasattr(exc, "status_code"):
        status_code = exc.status_code
    else:
        status_code = 500
        error_response["details"] = "Internal Server Error"
    
    return JSONResponse(
        status_code=status_code,
        content=error_response
    )

@app.on_event("startup")
async def startup_event():
    """Initialize application resources"""
    pass
