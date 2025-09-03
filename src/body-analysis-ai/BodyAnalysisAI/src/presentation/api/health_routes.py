"""
Presentation Layer - Health Check API Routes
FastAPI routes for service health and status monitoring
"""

from fastapi import APIRouter, Depends
import time
import logging
from datetime import datetime

from ..dto import HealthCheckResponseDto
from .dependencies import dependency_provider, DependencyProvider

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/health", tags=["health"])

# Global variable to track service start time
SERVICE_START_TIME = time.time()


def get_dependency_provider() -> DependencyProvider:
    """FastAPI dependency to get provider"""
    return dependency_provider


@router.get("/", response_model=HealthCheckResponseDto)
async def health_check(
    provider: DependencyProvider = Depends(get_dependency_provider)
):
    """
    Health check endpoint for service monitoring
    
    Returns:
        HealthCheckResponseDto containing service status and model information
    """
    try:
        # Calculate uptime
        uptime_seconds = time.time() - SERVICE_START_TIME
        
        # Get model status
        model_status = provider.get_model_status()
        
        # Check if service is ready
        is_ready = provider.is_ready()
        
        response = HealthCheckResponseDto(
            status="healthy" if is_ready else "initializing",
            timestamp=datetime.now().isoformat(),
            uptime_seconds=round(uptime_seconds, 2),
            models_loaded=model_status,
            service_ready=is_ready,
            version="2.0.0",
            environment="production"  # Could be from config
        )
        
        logger.debug(f"Health check completed: status={response.status}")
        return response
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        
        # Return degraded status instead of failing completely
        return HealthCheckResponseDto(
            status="degraded",
            timestamp=datetime.now().isoformat(),
            uptime_seconds=round(time.time() - SERVICE_START_TIME, 2),
            models_loaded={"error": str(e)},
            service_ready=False,
            version="2.0.0",
            environment="production",
            error_message=str(e)
        )


@router.get("/ready")
async def readiness_check(
    provider: DependencyProvider = Depends(get_dependency_provider)
):
    """
    Kubernetes-style readiness check
    
    Returns:
        Simple OK if service is ready to accept requests
    """
    try:
        if not provider.is_ready():
            await provider.initialize_dependencies()
        
        if provider.is_ready():
            return {"status": "ready"}
        else:
            return {"status": "not ready"}, 503
            
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return {"status": "error", "message": str(e)}, 503


@router.get("/live")
async def liveness_check():
    """
    Kubernetes-style liveness check
    
    Returns:
        Simple OK if service is alive (basic functionality)
    """
    return {"status": "alive", "timestamp": datetime.now().isoformat()}
