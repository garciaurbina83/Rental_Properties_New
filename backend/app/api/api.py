from fastapi import APIRouter
from app.api.endpoints import loans, contracts, tenants, reports, maintenance

api_router = APIRouter()

api_router.include_router(loans.router, prefix="/loans", tags=["loans"])
api_router.include_router(contracts.router, prefix="/contracts", tags=["contracts"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["maintenance"])
