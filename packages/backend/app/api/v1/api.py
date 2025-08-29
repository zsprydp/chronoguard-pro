from fastapi import APIRouter
from app.api.v1.endpoints import auth, appointments, patients, providers, analytics, optimization

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(providers.router, prefix="/providers", tags=["providers"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(optimization.router, prefix="/optimization", tags=["optimization"])