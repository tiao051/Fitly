"""
Domain Layer - Core Business Entities
Contains the fundamental business objects and rules

This __init__.py file serves as the public API for the entities package.
It imports and re-exports all entities for easy access.
"""

# Import all entities
from .body_type import BodyType
from .pose_keypoints import PoseKeypoints
from .body_ratios import BodyRatios
from .hybrid_features import DLEmbeddings, HybridFeatures
from .analysis_result import (
    BodyAnalysisResult,
    BodyAnalysisError,
    InsufficientKeypointsError,
    ModelLoadError,
    ImageProcessingError,
    InvalidImageError
)

# Define public API
__all__ = [
    # Core entities
    "BodyType",
    "PoseKeypoints", 
    "BodyRatios",
    "DLEmbeddings",
    "HybridFeatures",
    "BodyAnalysisResult",
    
    # Exceptions
    "BodyAnalysisError",
    "InsufficientKeypointsError", 
    "ModelLoadError",
    "ImageProcessingError",
    "InvalidImageError"
]
