"""
Presentation API - Public API
Main FastAPI router configuration
"""

from fastapi import APIRouter

# Import all route modules
from .analysis_routes import router as analysis_router
from .history_routes import router as history_router
from .health_routes import router as health_router

# Create main router
router = APIRouter()

# Include all sub-routers
router.include_router(analysis_router, prefix="/analysis", tags=["body-analysis"])
router.include_router(history_router, prefix="/history", tags=["analysis-history"])
router.include_router(health_router, tags=["health"])

# Public API exports
__all__ = [
    "router"
]
