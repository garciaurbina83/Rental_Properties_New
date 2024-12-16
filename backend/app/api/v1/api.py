from fastapi import APIRouter
from app.api.v1.endpoints import properties, tenants

api_router = APIRouter()

# Rutas de propiedades
api_router.include_router(
    properties.router,
    prefix="/properties",
    tags=["properties"]
)

# Rutas de inquilinos
api_router.include_router(
    tenants.router,
    prefix="/tenants",
    tags=["tenants"]
)