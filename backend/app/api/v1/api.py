from fastapi import APIRouter
from app.api.v1.endpoints import properties, tenants

api_router = APIRouter()

# Incluir todos los routers
api_router.include_router(properties.router, tags=["properties"])
api_router.include_router(tenants.router, tags=["tenants"])