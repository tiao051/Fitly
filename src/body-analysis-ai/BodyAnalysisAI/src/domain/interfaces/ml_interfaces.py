"""
Domain Interfaces - Machine Learning Features
Contracts for ML feature extraction and model services
"""

from abc import ABC, abstractmethod
from typing import Optional
import numpy as np

from ..entities import PoseKeypoints, HybridFeatures, BodyType


class IDLFeatureExtractor(ABC):
    """Interface for deep learning feature extraction"""
    
    @abstractmethod
    async def extract_features(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract deep learning features from image
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Feature vector if successful, None if failed
        """
        pass
    
    @abstractmethod
    def get_feature_dimension(self) -> int:
        """Get the dimension of extracted features"""
        pass
    
    @abstractmethod
    def is_model_loaded(self) -> bool:
        """Check if the feature extraction model is loaded"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> dict:
        """Get information about the feature extraction model"""
        pass


class IHybridClassifier(ABC):
    """Interface for hybrid body type classification"""
    
    @abstractmethod
    def create_hybrid_features(
        self, 
        dl_features: np.ndarray, 
        traditional_features: dict
    ) -> HybridFeatures:
        """
        Combine deep learning and traditional features
        
        Args:
            dl_features: Deep learning feature vector
            traditional_features: Traditional feature dictionary
            
        Returns:
            HybridFeatures object
        """
        pass
    
    @abstractmethod
    def classify_body_type(self, features: HybridFeatures) -> BodyType:
        """
        Classify body type from hybrid features
        
        Args:
            features: Combined feature representation
            
        Returns:
            Predicted body type
        """
        pass
    
    @abstractmethod
    def get_classification_confidence(self, features: HybridFeatures) -> float:
        """
        Get confidence score for classification
        
        Args:
            features: Combined feature representation
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        pass
    
    @abstractmethod
    def is_model_loaded(self) -> bool:
        """Check if the classification model is loaded"""
        pass


class IModelManager(ABC):
    """Interface for managing ML models"""
    
    @abstractmethod
    async def load_models(self) -> bool:
        """
        Load all required ML models
        
        Returns:
            True if all models loaded successfully
        """
        pass
    
    @abstractmethod
    def unload_models(self) -> None:
        """Unload all ML models to free memory"""
        pass
    
    @abstractmethod
    def get_model_status(self) -> dict[str, bool]:
        """
        Get loading status of all models
        
        Returns:
            Dictionary mapping model names to loaded status
        """
        pass
    
    @abstractmethod
    def validate_models(self) -> dict[str, bool]:
        """
        Validate that all models are working correctly
        
        Returns:
            Dictionary mapping model names to validation status
        """
        pass
