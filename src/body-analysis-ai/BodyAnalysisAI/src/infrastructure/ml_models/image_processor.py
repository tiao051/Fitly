"""
Infrastructure - Image Processor Implementation
Image preprocessing, validation and quality checks
"""

import cv2
import numpy as np
import logging
from typing import Optional, Tuple, Dict, List
from PIL import Image
import io

from ...domain.interfaces import IImageProcessor

logger = logging.getLogger(__name__)


class ImageProcessor(IImageProcessor):
    """Image processing and validation implementation"""
    
    def __init__(self):
        self.supported_formats = ['JPEG', 'JPG', 'PNG', 'BMP', 'TIFF', 'WEBP']
        self.max_image_size = 10 * 1024 * 1024  # 10MB
        self.min_dimension = 200  # Minimum width/height
        self.max_dimension = 4096  # Maximum width/height
    
    async def preprocess_image(self, image_data: bytes) -> Optional[np.ndarray]:
        """Preprocess raw image data for analysis"""
        try:
            # Validate format first
            if not self.validate_image_format(image_data):
                logger.warning("Invalid image format")
                return None
            
            # Convert bytes to numpy array
            image = self._bytes_to_numpy(image_data)
            if image is None:
                return None
            
            # Preprocess the image
            processed_image = self._preprocess_numpy_image(image)
            
            return processed_image
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {str(e)}")
            return None
    
    def _bytes_to_numpy(self, image_data: bytes) -> Optional[np.ndarray]:
        """Convert image bytes to numpy array"""
        try:
            # Use PIL to handle various formats
            pil_image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if needed
            if pil_image.mode in ('RGBA', 'LA'):
                # Create white background for transparency
                background = Image.new('RGB', pil_image.size, (255, 255, 255))
                background.paste(pil_image, mask=pil_image.split()[-1] if pil_image.mode == 'RGBA' else None)
                pil_image = background
            elif pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Convert to numpy array (RGB format)
            image_array = np.array(pil_image)
            
            return image_array
            
        except Exception as e:
            logger.error(f"Failed to convert image bytes to numpy: {str(e)}")
            return None
    
    def _preprocess_numpy_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess numpy image for analysis"""
        try:
            # Resize if too large
            image = self._resize_if_needed(image)
            
            # Ensure proper format (convert RGB to BGR for OpenCV compatibility)
            if len(image.shape) == 3 and image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Enhance image quality
            image = self._enhance_image(image)
            
            return image
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {str(e)}")
            return image  # Return original on error
    
    def _resize_if_needed(self, image: np.ndarray) -> np.ndarray:
        """Resize image if it exceeds maximum dimensions"""
        height, width = image.shape[:2]
        
        # Check if resizing is needed
        if max(height, width) <= self.max_dimension:
            return image
        
        # Calculate new dimensions maintaining aspect ratio
        if height > width:
            new_height = self.max_dimension
            new_width = int(width * (self.max_dimension / height))
        else:
            new_width = self.max_dimension
            new_height = int(height * (self.max_dimension / width))
        
        # Resize using high-quality interpolation
        resized_image = cv2.resize(
            image, 
            (new_width, new_height), 
            interpolation=cv2.INTER_LANCZOS4
        )
        
        logger.debug(f"Resized image from {width}x{height} to {new_width}x{new_height}")
        return resized_image
    
    def _enhance_image(self, image: np.ndarray) -> np.ndarray:
        """Apply basic image enhancement"""
        try:
            # Apply slight sharpening
            kernel = np.array([[-1,-1,-1], 
                             [-1, 9,-1], 
                             [-1,-1,-1]])
            enhanced = cv2.filter2D(image, -1, kernel * 0.1 + np.eye(3) * 0.9)
            
            # Ensure values are in valid range
            enhanced = np.clip(enhanced, 0, 255).astype(np.uint8)
            
            return enhanced
            
        except Exception as e:
            logger.warning(f"Image enhancement failed: {str(e)}")
            return image
    
    def validate_image_format(self, image_data: bytes) -> bool:
        """Validate if image format is supported"""
        try:
            # Check file size
            if len(image_data) > self.max_image_size:
                logger.warning(f"Image too large: {len(image_data)} bytes")
                return False
            
            if len(image_data) < 100:  # Too small to be a valid image
                logger.warning("Image data too small")
                return False
            
            # Try to open with PIL to validate format
            pil_image = Image.open(io.BytesIO(image_data))
            
            # Check format
            if pil_image.format not in self.supported_formats:
                logger.warning(f"Unsupported format: {pil_image.format}")
                return False
            
            # Check dimensions
            width, height = pil_image.size
            if width < self.min_dimension or height < self.min_dimension:
                logger.warning(f"Image too small: {width}x{height}")
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Image format validation failed: {str(e)}")
            return False
    
    def get_image_dimensions(self, image: np.ndarray) -> Tuple[int, int]:
        """Get image dimensions (width, height)"""
        if len(image.shape) >= 2:
            height, width = image.shape[:2]
            return width, height
        return 0, 0
    
    def resize_image(
        self, 
        image: np.ndarray, 
        target_size: Tuple[int, int]
    ) -> np.ndarray:
        """Resize image to target dimensions"""
        target_width, target_height = target_size
        return cv2.resize(
            image, 
            (target_width, target_height), 
            interpolation=cv2.INTER_LANCZOS4
        )
    
    def normalize_image(self, image: np.ndarray) -> np.ndarray:
        """Normalize image values for ML processing"""
        # Convert to float and normalize to [0, 1]
        normalized = image.astype(np.float32) / 255.0
        return normalized
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported image formats"""
        return self.supported_formats.copy()
    
    def get_max_image_size(self) -> int:
        """Get maximum allowed image size in bytes"""
        return self.max_image_size
    
    def validate_image_quality(self, image: np.ndarray) -> Dict:
        """Validate image quality for analysis"""
        try:
            height, width = image.shape[:2]
            
            # Calculate various quality metrics
            quality_metrics = {
                'dimensions': (width, height),
                'aspect_ratio': height / width if width > 0 else 0,
                'is_size_adequate': height >= self.min_dimension and width >= self.min_dimension,
                'is_aspect_ratio_ok': 0.5 <= (height / width) <= 3.0 if width > 0 else False,
            }
            
            # Check image sharpness (Laplacian variance)
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            quality_metrics['sharpness_score'] = float(laplacian_var)
            quality_metrics['is_sharp'] = laplacian_var > 100  # Threshold for acceptable sharpness
            
            # Check brightness
            mean_brightness = np.mean(gray)
            quality_metrics['brightness'] = float(mean_brightness)
            quality_metrics['is_brightness_ok'] = 30 <= mean_brightness <= 225
            
            # Overall quality assessment
            quality_metrics['is_suitable'] = all([
                quality_metrics['is_size_adequate'],
                quality_metrics['is_aspect_ratio_ok'],
                quality_metrics['is_sharp'],
                quality_metrics['is_brightness_ok']
            ])
            
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Quality validation failed: {str(e)}")
            return {
                'is_suitable': False,
                'error': str(e)
            }
