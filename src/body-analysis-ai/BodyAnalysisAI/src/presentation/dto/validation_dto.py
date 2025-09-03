"""
DTO - Validation Response Model
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any


class ValidationResponseDto(BaseModel):
    """Response model for image validation"""
    is_valid: bool = Field(
        ..., 
        description="Whether image is valid for analysis"
    )
    image_shape: List[int] = Field(
        ..., 
        description="Image dimensions [height, width, channels]"
    )
    image_dtype: str = Field(
        ..., 
        description="Image data type"
    )
    image_size_mb: float = Field(
        ..., 
        description="Image size in megabytes",
        ge=0.0
    )
    recommendations: List[str] = Field(
        default_factory=list, 
        description="Improvement recommendations"
    )
    quality_checks: Dict[str, Any] = Field(
        default_factory=dict,
        description="Detailed quality check results"
    )
    
    @classmethod
    def from_validation_result(cls, validation_result: Dict[str, Any]) -> "ValidationResponseDto":
        """Convert from use case validation result to DTO"""
        return cls(
            is_valid=validation_result["is_valid"],
            image_shape=validation_result["image_shape"],
            image_dtype=validation_result["image_dtype"],
            image_size_mb=validation_result.get("image_size_mb", 0.0),
            recommendations=validation_result.get("recommendations", []),
            quality_checks=validation_result.get("quality_checks", {})
        )
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "is_valid": True,
                "image_shape": [512, 384, 3],
                "image_dtype": "uint8",
                "image_size_mb": 0.15,
                "recommendations": [],
                "quality_checks": {
                    "resolution": {
                        "width": 384,
                        "height": 512,
                        "is_adequate": True
                    },
                    "brightness": {
                        "mean_brightness": 128.5,
                        "is_adequate": True
                    },
                    "contrast": {
                        "std_deviation": 45.2,
                        "is_adequate": True
                    }
                }
            }
        }
