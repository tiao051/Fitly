"""
Domain Interfaces - Public API
Clean imports for all domain interface contracts
"""

# Pose extraction interface
from .pose_extractor import IPoseExtractor

# Ratio calculation interface  
from .ratio_calculator import IRatioCalculator

# Machine learning interfaces
from .ml_interfaces import (
    IDLFeatureExtractor,
    IHybridClassifier,
    IModelManager
)

# Repository interfaces
from .repository_interfaces import (
    IAnalysisRepository,
    IImageRepository
)

# Image processing interface
from .image_processor import IImageProcessor

# Public interface exports
__all__ = [
    # Pose detection
    "IPoseExtractor",
    
    # Body measurements
    "IRatioCalculator", 
    
    # Machine learning
    "IDLFeatureExtractor",
    "IHybridClassifier", 
    "IModelManager",
    
    # Data persistence
    "IAnalysisRepository",
    "IImageRepository",
    
    # Image processing
    "IImageProcessor"
]
