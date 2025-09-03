"""
Domain Entity - Analysis Result and Exceptions
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from .body_type import BodyType
from .pose_keypoints import PoseKeypoints
from .body_ratios import BodyRatios
from .hybrid_features import DLEmbeddings


@dataclass
class BodyAnalysisResult:
    """Complete body analysis result"""
    body_type: BodyType
    confidence_score: float
    pose_keypoints: PoseKeypoints
    body_ratios: BodyRatios
    dl_embeddings: Optional[DLEmbeddings]
    processing_metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for API response"""
        return {
            "body_type": self.body_type.value,
            "confidence_score": self.confidence_score,
            "body_ratios": {
                "shoulder_to_hip_ratio": self.body_ratios.shoulder_to_hip_ratio,
                "waist_to_hip_ratio": self.body_ratios.waist_to_hip_ratio,
                "shoulder_to_waist_ratio": self.body_ratios.shoulder_to_waist_ratio,
                "torso_aspect_ratio": self.body_ratios.torso_aspect_ratio
            },
            "keypoints_detected": len(self.pose_keypoints.keypoints),
            "detection_confidence": self.pose_keypoints.detection_confidence,
            "processing_metadata": self.processing_metadata
        }
    
    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """Check if result has high confidence"""
        return self.confidence_score >= threshold
    
    def validate_result(self) -> bool:
        """Validate the analysis result"""
        return (
            0.0 <= self.confidence_score <= 1.0 and
            self.body_ratios.validate_ratios() and
            len(self.pose_keypoints.keypoints) > 0
        )


# Custom Exceptions
class BodyAnalysisError(Exception):
    """Custom exception for body analysis errors"""
    pass


class InsufficientKeypointsError(BodyAnalysisError):
    """Raised when not enough keypoints are detected"""
    pass


class ModelLoadError(BodyAnalysisError):
    """Raised when ML models fail to load"""
    pass


class ImageProcessingError(BodyAnalysisError):
    """Raised when image processing fails"""
    pass


class InvalidImageError(BodyAnalysisError):
    """Raised when image format is invalid"""
    pass
