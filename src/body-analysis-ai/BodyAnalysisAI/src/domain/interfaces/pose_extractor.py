"""
Domain Interface - Pose Extraction
Contract for pose keypoint extraction services
"""

from abc import ABC, abstractmethod
from typing import Optional
import numpy as np

from ..entities import PoseKeypoints


class IPoseExtractor(ABC):
    """Interface for pose keypoint extraction"""
    
    @abstractmethod
    async def extract_keypoints(self, image: np.ndarray) -> Optional[PoseKeypoints]:
        """
        Extract pose keypoints from image
        
        Args:
            image: Input image as numpy array
            
        Returns:
            PoseKeypoints object if successful, None if failed
        """
        pass
    
    @abstractmethod
    def validate_keypoints(self, keypoints: PoseKeypoints) -> bool:
        """
        Validate if keypoints are sufficient for analysis
        
        Args:
            keypoints: Extracted pose keypoints
            
        Returns:
            True if keypoints are sufficient for body analysis
        """
        pass
    
    @abstractmethod
    def get_model_version(self) -> str:
        """Get the version/name of the pose extraction model"""
        pass
    
    @abstractmethod
    def is_model_loaded(self) -> bool:
        """Check if the pose extraction model is loaded and ready"""
        pass
    
    @abstractmethod
    def get_required_keypoints(self) -> list[str]:
        """Get list of keypoints required for body analysis"""
        pass
