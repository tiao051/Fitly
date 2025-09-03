"""
DTO - History and Trends Response Models
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any
from .analysis_dto import AnalysisResponseDto


class AnalysisHistoryItemDto(BaseModel):
    """Single analysis item in history"""
    analysis_id: str = Field(..., description="Analysis identifier")
    body_type: str = Field(..., description="Classified body type")
    confidence_score: float = Field(..., description="Classification confidence", ge=0.0, le=1.0)
    timestamp: str = Field(..., description="Analysis timestamp")
    body_ratios: Dict[str, float] = Field(..., description="Body ratios")
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "analysis_id": "123e4567-e89b-12d3-a456-426614174000",
                "body_type": "hourglass",
                "confidence_score": 0.92,
                "timestamp": "2025-09-04T10:30:00",
                "body_ratios": {
                    "shoulder_to_hip_ratio": 1.05,
                    "waist_to_hip_ratio": 0.75,
                    "shoulder_to_waist_ratio": 1.4,
                    "torso_aspect_ratio": 2.1
                }
            }
        }


class AnalysisHistoryDto(BaseModel):
    """Response model for analysis history"""
    user_id: str = Field(..., description="User identifier")
    total_analyses: int = Field(..., description="Total number of analyses", ge=0)
    analyses: List[AnalysisHistoryItemDto] = Field(
        ..., 
        description="List of analysis results"
    )
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "total_analyses": 5,
                "analyses": [
                    {
                        "analysis_id": "123e4567-e89b-12d3-a456-426614174000",
                        "body_type": "hourglass",
                        "confidence_score": 0.92,
                        "timestamp": "2025-09-04T10:30:00",
                        "body_ratios": {
                            "shoulder_to_hip_ratio": 1.05,
                            "waist_to_hip_ratio": 0.75,
                            "shoulder_to_waist_ratio": 1.4,
                            "torso_aspect_ratio": 2.1
                        }
                    }
                ]
            }
        }


class TrendsResponseDto(BaseModel):
    """Response model for user analysis trends"""
    user_id: str = Field(..., description="User identifier")
    analysis_period_days: int = Field(..., description="Analysis period in days", ge=1)
    trends: Dict[str, Any] = Field(..., description="Trend analysis data")
    message: str = Field(..., description="Status message")
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "analysis_period_days": 30,
                "trends": {
                    "total_analyses": 8,
                    "most_common_body_type": "hourglass",
                    "average_confidence": 0.89,
                    "consistency_score": 0.75,
                    "recent_body_type": "hourglass",
                    "body_type_distribution": {
                        "hourglass": 6,
                        "pear": 2
                    },
                    "confidence_metrics": {
                        "average": 0.89,
                        "minimum": 0.72,
                        "maximum": 0.96
                    }
                },
                "message": "Trends calculated successfully"
            }
        }
