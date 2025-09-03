"""
Domain Layer - Business Interfaces
Defines contracts for external dependencies
"""

from abc import ABC, abstractmethod
from typing import Optional, List
import numpy as np

from ..entities import (
    PoseKeypoints, 
    BodyRatios, 
    DLEmbeddings, 
    HybridFeatures, 
    BodyType, 
    BodyAnalysisResult
)


class IPoseExtractor(ABC):
    """Interface for pose keypoint extraction"""
    
    @abstractmethod
    async def extract_keypoints(self, image: np.ndarray) -> Optional[PoseKeypoints]:
        """Extract pose keypoints from image"""
        pass
    
    @abstractmethod
    def validate_keypoints(self, keypoints: PoseKeypoints) -> bool:
        """Validate if keypoints are sufficient for analysis"""
        pass


class IRatioCalculator(ABC):
    """Interface for body ratio calculation"""
    
    @abstractmethod
    def calculate_ratios(self, keypoints: PoseKeypoints) -> BodyRatios:
        """Calculate body ratios from pose keypoints"""
        pass


class IDLFeatureExtractor(ABC):
    """Interface for deep learning feature extraction"""
    
    @abstractmethod
    async def extract_embeddings(self, image: np.ndarray) -> DLEmbeddings:
        """Extract embeddings using pretrained DL backbone"""
        pass
    
    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """Get dimension of embeddings"""
        pass


class IHybridClassifier(ABC):
    """Interface for hybrid feature classification"""
    
    @abstractmethod
    async def classify(self, features: HybridFeatures) -> tuple[BodyType, float]:
        """Classify body type from hybrid features"""
        pass
    
    @abstractmethod
    def is_model_loaded(self) -> bool:
        """Check if classification model is loaded"""
        pass


class IAnalysisRepository(ABC):
    """Interface for storing analysis results"""
    
    @abstractmethod
    async def save_result(self, result: BodyAnalysisResult, user_id: Optional[str] = None) -> str:
        """Save analysis result and return result ID"""
        pass
    
    @abstractmethod
    async def get_result(self, result_id: str) -> Optional[BodyAnalysisResult]:
        """Retrieve analysis result by ID"""
        pass
    
    @abstractmethod
    async def get_user_history(self, user_id: str, limit: int = 10) -> List[BodyAnalysisResult]:
        """Get user's analysis history"""
        pass


class IImageProcessor(ABC):
    """Interface for image preprocessing"""
    
    @abstractmethod
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for analysis"""
        pass
    
    @abstractmethod
    def validate_image(self, image: np.ndarray) -> bool:
        """Validate image quality and format"""
        pass
