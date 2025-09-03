"""
Application Use Case - Validate Image
Validate image quality and format before analysis
"""

from typing import Dict, Any
import logging
import numpy as np

from ...domain.entities import BodyAnalysisError
from ...domain.interfaces import IImageProcessor

logger = logging.getLogger(__name__)


class ValidateImageUseCase:
    """Use case for image validation before analysis"""
    
    def __init__(self, image_processor: IImageProcessor):
        self.image_processor = image_processor
    
    def execute(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Validate image and return validation result
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Dictionary containing validation results and recommendations
            
        Raises:
            BodyAnalysisError: If validation process fails
        """
        try:
            if image is None:
                raise ValueError("Image cannot be None")
            
            if len(image.shape) not in [2, 3]:
                raise ValueError("Image must be 2D (grayscale) or 3D (color)")
            
            is_valid = self.image_processor.validate_image(image)
            
            validation_result = {
                "is_valid": is_valid,
                "image_shape": image.shape,
                "image_dtype": str(image.dtype),
                "image_size_mb": image.nbytes / (1024 * 1024),
                "recommendations": [],
                "quality_checks": self._perform_quality_checks(image)
            }
            
            if not is_valid:
                validation_result["recommendations"].extend([
                    "Ensure image shows full torso (shoulders to hips)",
                    "Use good lighting and clear background", 
                    "Person should face the camera directly",
                    "Image should be at least 224x224 pixels",
                    "Avoid blurry or low-resolution images"
                ])
            
            logger.info(f"Image validation completed: valid={is_valid}")
            return validation_result
            
        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Image validation failed: {str(e)}")
            raise BodyAnalysisError(f"Validation failed: {str(e)}") from e
    
    def _perform_quality_checks(self, image: np.ndarray) -> Dict[str, Any]:
        """Perform additional quality checks on the image"""
        checks = {}
        
        try:
            # Resolution check
            height, width = image.shape[:2]
            checks["resolution"] = {
                "width": width,
                "height": height,
                "is_adequate": width >= 224 and height >= 224
            }
            
            # Brightness check
            if len(image.shape) == 3:
                brightness = np.mean(image)
            else:
                brightness = np.mean(image)
            
            checks["brightness"] = {
                "mean_brightness": float(brightness),
                "is_adequate": 50 <= brightness <= 200  # Reasonable range
            }
            
            # Contrast check (standard deviation)
            contrast = np.std(image)
            checks["contrast"] = {
                "std_deviation": float(contrast),
                "is_adequate": contrast > 20  # Sufficient contrast
            }
            
        except Exception as e:
            logger.warning(f"Quality checks failed: {str(e)}")
            checks["error"] = str(e)
        
        return checks
