"""
Presentation Layer - Data Transfer Objects
Defines request/response models for API
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


class BodyTypeResponse(str, Enum):
    """Body type options for API response"""
    HOURGLASS = "hourglass"
    APPLE = "apple"
    PEAR = "pear"
    RECTANGLE = "rectangle"
    INVERTED_TRIANGLE = "inverted_triangle"


class BodyRatiosDto(BaseModel):
    """Body ratios data transfer object"""
    shoulder_to_hip_ratio: float = Field(..., description="Shoulder width to hip width ratio")
    waist_to_hip_ratio: float = Field(..., description="Waist width to hip width ratio")
    shoulder_to_waist_ratio: float = Field(..., description="Shoulder width to waist width ratio")
    torso_aspect_ratio: float = Field(..., description="Torso height to shoulder width ratio")


class AnalysisRequestDto(BaseModel):
    """Request model for body analysis"""
    user_id: Optional[str] = Field(None, description="Optional user identifier")
    save_result: bool = Field(True, description="Whether to save the analysis result")


class AnalysisResponseDto(BaseModel):
    """Response model for body analysis"""
    body_type: BodyTypeResponse = Field(..., description="Classified body type")
    confidence_score: float = Field(..., description="Classification confidence (0-1)")
    body_ratios: BodyRatiosDto = Field(..., description="Calculated body ratios")
    keypoints_detected: int = Field(..., description="Number of pose keypoints detected")
    detection_confidence: float = Field(..., description="Pose detection confidence")
    processing_metadata: Dict[str, Any] = Field(..., description="Processing metadata")
    result_id: Optional[str] = Field(None, description="Result ID if saved")


class ValidationResponseDto(BaseModel):
    """Response model for image validation"""
    is_valid: bool = Field(..., description="Whether image is valid for analysis")
    image_shape: List[int] = Field(..., description="Image dimensions [height, width, channels]")
    image_dtype: str = Field(..., description="Image data type")
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")


class AnalysisHistoryDto(BaseModel):
    """Response model for analysis history"""
    total_results: int = Field(..., description="Total number of analysis results")
    results: List[AnalysisResponseDto] = Field(..., description="List of analysis results")


class TrendsResponseDto(BaseModel):
    """Response model for user analysis trends"""
    total_analyses: int = Field(..., description="Total number of analyses")
    most_common_body_type: str = Field(..., description="Most frequently classified body type")
    average_confidence: float = Field(..., description="Average classification confidence")
    recent_body_type: str = Field(..., description="Most recent body type classification")
    consistency_score: float = Field(..., description="Consistency of classifications (0-1)")


class HealthCheckResponseDto(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Service health status")
    version: str = Field(..., description="API version")
    models_loaded: Dict[str, bool] = Field(..., description="Model loading status")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")


class ErrorResponseDto(BaseModel):
    """Response model for errors"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
