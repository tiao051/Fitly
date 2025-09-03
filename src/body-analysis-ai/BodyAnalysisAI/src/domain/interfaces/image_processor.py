"""
Domain Interface - Image Processing
Contract for image processing and validation services
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple
import numpy as np


class IImageProcessor(ABC):
    """Interface for image processing operations"""
    
    @abstractmethod
    async def preprocess_image(self, image_data: bytes) -> Optional[np.ndarray]:
        """
        Preprocess raw image data for analysis
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Processed image as numpy array if successful, None if failed
        """
        pass
    
    @abstractmethod
    def validate_image_format(self, image_data: bytes) -> bool:
        """
        Validate if image format is supported
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            True if format is supported for analysis
        """
        pass
    
    @abstractmethod
    def get_image_dimensions(self, image: np.ndarray) -> Tuple[int, int]:
        """
        Get image dimensions
        
        Args:
            image: Image as numpy array
            
        Returns:
            Tuple of (width, height)
        """
        pass
    
    @abstractmethod
    def resize_image(
        self, 
        image: np.ndarray, 
        target_size: Tuple[int, int]
    ) -> np.ndarray:
        """
        Resize image to target dimensions
        
        Args:
            image: Input image
            target_size: Target (width, height)
            
        Returns:
            Resized image
        """
        pass
    
    @abstractmethod
    def normalize_image(self, image: np.ndarray) -> np.ndarray:
        """
        Normalize image values for ML processing
        
        Args:
            image: Input image
            
        Returns:
            Normalized image
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> list[str]:
        """Get list of supported image formats"""
        pass
    
    @abstractmethod
    def get_max_image_size(self) -> int:
        """Get maximum allowed image size in bytes"""
        pass
    
    @abstractmethod
    def validate_image_quality(self, image: np.ndarray) -> dict:
        """
        Validate image quality for analysis
        
        Args:
            image: Image to validate
            
        Returns:
            Dictionary with quality metrics and validation results
        """
        pass
