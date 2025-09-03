"""
DTO - Analysis Request/Response Models
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from .body_type_dto import BodyTypeResponse
from .body_ratios_dto import BodyRatiosDto


class AnalysisRequestDto(BaseModel):
    """Request model for body analysis"""
    user_id: Optional[str] = Field(
        None, 
        description="Optional user identifier",
        min_length=1,
        max_length=100
    )
    save_result: bool = Field(
        True, 
        description="Whether to save the analysis result"
    )
    
    @validator('user_id')
    def validate_user_id(cls, v):
        """Validate user_id format"""
        if v is not None and not v.strip():
            raise ValueError('user_id cannot be empty string')
        return v.strip() if v else None


class AnalysisResponseDto(BaseModel):
    """Response model for body analysis"""
    body_type: BodyTypeResponse = Field(
        ..., 
        description="Classified body type"
    )
    confidence_score: float = Field(
        ..., 
        description="Classification confidence (0-1)",
        ge=0.0,
        le=1.0
    )
    body_ratios: BodyRatiosDto = Field(
        ..., 
        description="Calculated body ratios"
    )
    keypoints_detected: int = Field(
        ..., 
        description="Number of pose keypoints detected",
        ge=0
    )
    detection_confidence: float = Field(
        ..., 
        description="Pose detection confidence",
        ge=0.0,
        le=1.0
    )
    processing_metadata: Dict[str, Any] = Field(
        ..., 
        description="Processing metadata"
    )
    result_id: Optional[str] = Field(
        None, 
        description="Result ID if saved"
    )
    
    @classmethod
    def from_domain(cls, result, result_id: Optional[str] = None) -> "AnalysisResponseDto":
        """Convert from domain BodyAnalysisResult to DTO"""
        return cls(
            body_type=BodyTypeResponse.from_domain_type(result.body_type),
            confidence_score=result.confidence_score,
            body_ratios=BodyRatiosDto.from_domain(result.body_ratios),
            keypoints_detected=len(result.pose_keypoints.keypoints),
            detection_confidence=result.pose_keypoints.detection_confidence,
            processing_metadata=result.processing_metadata,
            result_id=result_id or result.processing_metadata.get("analysis_id")
        )
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "body_type": "hourglass",
                "confidence_score": 0.92,
                "body_ratios": {
                    "shoulder_to_hip_ratio": 1.05,
                    "waist_to_hip_ratio": 0.75,
                    "shoulder_to_waist_ratio": 1.4,
                    "torso_aspect_ratio": 2.1
                },
                "keypoints_detected": 17,
                "detection_confidence": 0.88,
                "processing_metadata": {
                    "analysis_id": "123e4567-e89b-12d3-a456-426614174000",
                    "processing_time_seconds": 1.23,
                    "timestamp": "2025-09-04T10:30:00"
                },
                "result_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
