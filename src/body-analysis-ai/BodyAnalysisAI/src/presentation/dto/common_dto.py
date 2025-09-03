"""
DTO - Health Check and Error Response Models
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class HealthCheckResponseDto(BaseModel):
    """Response model for health check"""
    status: str = Field(
        ..., 
        description="Service health status (healthy, initializing, degraded)"
    )
    timestamp: str = Field(
        ..., 
        description="Current timestamp"
    )
    uptime_seconds: float = Field(
        ..., 
        description="Service uptime in seconds",
        ge=0.0
    )
    models_loaded: Dict[str, Any] = Field(
        ..., 
        description="Model loading status"
    )
    service_ready: bool = Field(
        ..., 
        description="Whether service is ready to accept requests"
    )
    version: str = Field(
        ..., 
        description="API version"
    )
    environment: str = Field(
        ..., 
        description="Environment name"
    )
    error_message: Optional[str] = Field(
        None, 
        description="Error message if status is degraded"
    )
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-09-04T10:30:00",
                "uptime_seconds": 3600.5,
                "models_loaded": {
                    "pose_extractor": True,
                    "dl_extractor": True,
                    "classifier": True
                },
                "service_ready": True,
                "version": "2.0.0",
                "environment": "production"
            }
        }


class ErrorResponseDto(BaseModel):
    """Response model for errors"""
    error: str = Field(
        ..., 
        description="Error type/category"
    )
    message: str = Field(
        ..., 
        description="Human-readable error message"
    )
    details: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional error details"
    )
    timestamp: str = Field(
        ..., 
        description="Error timestamp"
    )
    request_id: Optional[str] = Field(
        None,
        description="Request identifier for tracking"
    )
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "error": "InsufficientKeypointsError",
                "message": "Not enough keypoints detected for reliable analysis",
                "details": {
                    "keypoints_detected": 8,
                    "minimum_required": 12
                },
                "timestamp": "2025-09-04T10:30:00",
                "request_id": "req_123456"
            }
        }
