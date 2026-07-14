from fastapi import APIRouter

from backend.api.routes import cameras, traffic, signals, emergencies, plates, analytics

api_router = APIRouter()

api_router.include_router(cameras.router, prefix="/cameras", tags=["Cameras"])
api_router.include_router(traffic.router, prefix="/traffic", tags=["Traffic Records"])
api_router.include_router(signals.router, prefix="/signals", tags=["Signals"])
api_router.include_router(emergencies.router, prefix="/emergencies", tags=["Emergencies"])
api_router.include_router(plates.router, prefix="/plates", tags=["Number Plates"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
