"""
DTO - Body Ratios Data Transfer Object
"""

from pydantic import BaseModel, Field


class BodyRatiosDto(BaseModel):
    """Body ratios data transfer object"""
    shoulder_to_hip_ratio: float = Field(
        ..., 
        description="Shoulder width to hip width ratio",
        ge=0.0,
        le=5.0
    )
    waist_to_hip_ratio: float = Field(
        ..., 
        description="Waist width to hip width ratio",
        ge=0.0,
        le=2.0
    )
    shoulder_to_waist_ratio: float = Field(
        ..., 
        description="Shoulder width to waist width ratio",
        ge=0.0,
        le=3.0
    )
    torso_aspect_ratio: float = Field(
        ..., 
        description="Torso height to shoulder width ratio",
        ge=0.0,
        le=10.0
    )
    
    @classmethod
    def from_domain(cls, body_ratios) -> "BodyRatiosDto":
        """Convert from domain BodyRatios to DTO"""
        return cls(
            shoulder_to_hip_ratio=body_ratios.shoulder_to_hip_ratio,
            waist_to_hip_ratio=body_ratios.waist_to_hip_ratio,
            shoulder_to_waist_ratio=body_ratios.shoulder_to_waist_ratio,
            torso_aspect_ratio=body_ratios.torso_aspect_ratio
        )
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "shoulder_to_hip_ratio": 1.05,
                "waist_to_hip_ratio": 0.75,
                "shoulder_to_waist_ratio": 1.4,
                "torso_aspect_ratio": 2.1
            }
        }
