"""
Domain Layer - Core Business Entities
Contains the fundamental business objects and rules
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import numpy as np


class BodyType(Enum):
    """Body type classification categories"""
    HOURGLASS = "hourglass"      # X-shape: shoulders ≈ hips, small waist
    APPLE = "apple"              # O-shape: fuller midsection
    PEAR = "pear"                # A-shape: hips > shoulders
    RECTANGLE = "rectangle"      # H-shape: shoulders ≈ waist ≈ hips
    INVERTED_TRIANGLE = "inverted_triangle"  # V-shape: shoulders > hips


@dataclass
class PoseKeypoints:
    """Pose keypoints detected from image"""
    keypoints: Dict[str, Tuple[float, float, float]]  # name -> (x, y, confidence)
    image_dimensions: Tuple[int, int]  # (width, height)
    detection_confidence: float
    
    def get_keypoint(self, name: str) -> Optional[Tuple[float, float, float]]:
        """Get specific keypoint coordinates and confidence"""
        return self.keypoints.get(name)
    
    def is_keypoint_valid(self, name: str, min_confidence: float = 0.5) -> bool:
        """Check if keypoint meets confidence threshold"""
        keypoint = self.get_keypoint(name)
        return keypoint is not None and keypoint[2] >= min_confidence


@dataclass
class BodyRatios:
    """Body measurement ratios extracted from pose"""
    shoulder_to_hip_ratio: float
    waist_to_hip_ratio: float
    shoulder_to_waist_ratio: float
    torso_aspect_ratio: float
    
    def to_feature_vector(self) -> np.ndarray:
        """Convert ratios to feature vector for ML"""
        return np.array([
            self.shoulder_to_hip_ratio,
            self.waist_to_hip_ratio,
            self.shoulder_to_waist_ratio,
            self.torso_aspect_ratio
        ])


@dataclass
class DLEmbeddings:
    """Deep learning embeddings from pretrained backbone"""
    embeddings: np.ndarray
    model_name: str
    embedding_dimension: int
    
    def get_features(self) -> np.ndarray:
        """Get embedding features as numpy array"""
        return self.embeddings


@dataclass
class HybridFeatures:
    """Combined features from DL embeddings and pose ratios"""
    dl_embeddings: DLEmbeddings
    body_ratios: BodyRatios
    
    def to_combined_vector(self) -> np.ndarray:
        """Combine both feature types into single vector"""
        dl_features = self.dl_embeddings.get_features()
        ratio_features = self.body_ratios.to_feature_vector()
        return np.concatenate([dl_features, ratio_features])


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


class BodyAnalysisError(Exception):
    """Custom exception for body analysis errors"""
    pass


class InsufficientKeypointsError(BodyAnalysisError):
    """Raised when not enough keypoints are detected"""
    pass


class ModelLoadError(BodyAnalysisError):
    """Raised when ML models fail to load"""
    pass
