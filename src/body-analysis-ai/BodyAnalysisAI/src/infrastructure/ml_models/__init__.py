"""
Infrastructure ML Models - Public API
Clean imports for all ML model implementations
"""

# Pose extraction implementation
from .yolo_pose_extractor import YOLOPoseExtractor

# Body ratio calculation implementation  
from .ratio_calculator import BodyRatioCalculator

# Deep learning feature extraction implementation
# from .resnet_extractor import ResNetFeatureExtractor  # Temporarily disabled

# Hybrid classification implementation
from .hybrid_classifier import SVMHybridClassifier

# Image processing implementation
from .image_processor import ImageProcessor

# Model management implementation
from .model_manager import MLModelManager

# Public API exports
__all__ = [
    # Pose detection
    "YOLOPoseExtractor",
    
    # Body measurements
    "BodyRatioCalculator",
    
    # Machine learning
    # "ResNetFeatureExtractor",  # Temporarily disabled
    "SVMHybridClassifier",
    
    # Image processing
    "ImageProcessor",
    
    # Model management
    "MLModelManager"
]
