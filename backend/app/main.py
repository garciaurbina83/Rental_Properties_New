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
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    # API de Gestión de Propiedades en Alquiler

    Esta API proporciona endpoints para gestionar propiedades en alquiler, incluyendo:
    
    * Gestión de propiedades
    * Gestión de inquilinos
    * Gestión de contratos
    * Gestión de pagos
    * Reportes y estadísticas
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

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos
    allow_headers=["*"],  # Permite todos los headers
)

# Incluir rutas de la API
app.include_router(api_router, prefix=settings.API_V1_STR)

# Para debugging - imprimir todas las rutas registradas
@app.on_event("startup")
async def print_routes():
    """Print all registered routes for debugging"""
    print("\n=== Registered Routes ===")
    for route in app.routes:
        print(f"Route: {route.path}, Methods: {route.methods}")
    print("=======================\n")

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
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        title=f"{settings.APP_NAME} - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
    )

@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        title=f"{settings.APP_NAME} - ReDoc",
    )

@app.get("/")
async def root():
    """
    Endpoint de salud para verificar que la API está funcionando

    Returns:
        dict: Estado actual de la API
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "OK",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    return {"status": "OK"}

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
    
    # Log the error here if needed
    print(f"Error: {error_response}")
    
    return JSONResponse(
        status_code=500,
        content=error_response
    )

@app.on_event("startup")
async def startup_event():
    """Initialize application resources"""
    # Initialize database
    from app.core.database import init_db
    await init_db()
