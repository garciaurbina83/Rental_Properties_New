from fastapi import APIRouter
from .endpoints import (
    properties, units, tenants, contracts, 
    payments, reports, integrations, audit, 
    receipts, vendors, expenses, loans
)

api_router = APIRouter()

api_router.include_router(
    properties.router,
    prefix="/properties",
    tags=["properties"]
)

api_router.include_router(
    units.router,
    prefix="/units",
    tags=["units"]
)

api_router.include_router(
    tenants.router,
    prefix="/tenants",
    tags=["tenants"]
)

api_router.include_router(
    contracts.router,
    prefix="/contracts",
    tags=["contracts"]
)

api_router.include_router(
    payments.router,
    prefix="/payments",
    tags=["payments"]
)

api_router.include_router(
    reports.router,
    prefix="/reports",
    tags=["reports"]
)

api_router.include_router(
    integrations.router,
    prefix="/integrations",
    tags=["integrations"]
)

api_router.include_router(
    audit.router,
    prefix="/audit",
    tags=["audit"]
)

api_router.include_router(
    receipts.router,
    prefix="/receipts",
    tags=["receipts"]
)

api_router.include_router(
    vendors.router,
    prefix="/vendors",
    tags=["vendors"]
)

api_router.include_router(
    expenses.router,
    prefix="/expenses",
    tags=["expenses"]
)

api_router.include_router(
    loans.router,
    prefix="/loans",
    tags=["loans"]
)
