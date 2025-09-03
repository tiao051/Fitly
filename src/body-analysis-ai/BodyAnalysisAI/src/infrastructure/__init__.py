"""
Infrastructure Layer - External Dependencies and Implementations
Clean imports for all infrastructure components
"""

# ML Models implementations
from .ml_models import (
    YOLOPoseExtractor,
    BodyRatioCalculator,
    # ResNetFeatureExtractor,  # Temporarily disabled
    SVMHybridClassifier,
    ImageProcessor,
    MLModelManager
)

# Repository implementations
from .repositories import (
    InMemoryAnalysisRepository,
    FileBasedAnalysisRepository,
    FileBasedImageRepository
)

# Public API exports
__all__ = [
    # ML Models
    "YOLOPoseExtractor",
    "BodyRatioCalculator", 
    # "ResNetFeatureExtractor",  # Temporarily disabled
    "SVMHybridClassifier",
    "ImageProcessor",
    "MLModelManager",
    
    # Repositories
    "InMemoryAnalysisRepository",
    "FileBasedAnalysisRepository",
    "FileBasedImageRepository"
]