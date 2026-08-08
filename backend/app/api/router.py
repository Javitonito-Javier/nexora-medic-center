from fastapi import APIRouter

from app.api.routes import (
    appointments,
    attachments,
    audit,
    auth,
    business,
    cash_registers,
    consultations,
    dashboard,
    inventory,
    license,
    patients,
    pharmacy,
    points,
    prescriptions,
    receipts,
    reports,
    users,
)

api_router = APIRouter()
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(attachments.router, tags=["attachments"])
api_router.include_router(license.router, prefix="/license", tags=["license"])
api_router.include_router(business.router, prefix="/business", tags=["business"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
api_router.include_router(consultations.router, prefix="/consultations", tags=["consultations"])
api_router.include_router(prescriptions.router, prefix="/prescriptions", tags=["prescriptions"])
api_router.include_router(cash_registers.router, prefix="/cash-registers", tags=["cash registers"])
api_router.include_router(receipts.router, prefix="/receipts", tags=["receipts"])
api_router.include_router(pharmacy.router, prefix="/pharmacy", tags=["pharmacy"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(points.router, prefix="/points", tags=["points"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
