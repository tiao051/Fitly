"""
Infrastructure - Body Ratio Calculator Implementation  
Calculates body proportions from pose keypoints
"""

import numpy as np
import logging
from typing import Dict, Tuple

from ...domain.entities import PoseKeypoints, BodyRatios, InsufficientKeypointsError
from ...domain.interfaces import IRatioCalculator

logger = logging.getLogger(__name__)


class BodyRatioCalculator(IRatioCalculator):
    """Calculate body ratios from pose keypoints implementation"""
    
    def __init__(self):
        self.ratio_ranges = {
            'shoulder_to_hip_ratio': (0.8, 1.8),
            'waist_to_hip_ratio': (0.6, 1.0),
            'shoulder_to_waist_ratio': (1.0, 2.0),
            'torso_aspect_ratio': (0.5, 2.0)
        }
    
    def calculate_ratios(self, keypoints: PoseKeypoints) -> BodyRatios:
        """Calculate body ratios from pose keypoints"""
        try:
            # Get essential body landmarks
            left_shoulder = keypoints.get_keypoint('left_shoulder')
            right_shoulder = keypoints.get_keypoint('right_shoulder')
            left_hip = keypoints.get_keypoint('left_hip')
            right_hip = keypoints.get_keypoint('right_hip')
            
            if not all([left_shoulder, right_shoulder, left_hip, right_hip]):
                missing = [name for name, point in [
                    ('left_shoulder', left_shoulder),
                    ('right_shoulder', right_shoulder),
                    ('left_hip', left_hip),
                    ('right_hip', right_hip)
                ] if not point]
                raise InsufficientKeypointsError(
                    f"Missing essential keypoints for ratio calculation: {missing}"
                )
            
            # Calculate body measurements
            shoulder_width = self._calculate_distance(left_shoulder, right_shoulder)
            hip_width = self._calculate_distance(left_hip, right_hip)
            
            # Estimate waist width (anatomically ~70-80% of hip width)
            waist_width = hip_width * 0.75
            
            # Calculate torso length (vertical distance from shoulders to hips)
            shoulder_center_y = (left_shoulder[1] + right_shoulder[1]) / 2
            hip_center_y = (left_hip[1] + right_hip[1]) / 2
            torso_height = abs(hip_center_y - shoulder_center_y)
            
            # Calculate body ratios
            shoulder_to_hip_ratio = self._safe_divide(shoulder_width, hip_width, 1.0)
            waist_to_hip_ratio = self._safe_divide(waist_width, hip_width, 0.75)
            shoulder_to_waist_ratio = self._safe_divide(shoulder_width, waist_width, 1.33)
            torso_aspect_ratio = self._safe_divide(torso_height, shoulder_width, 1.0)
            
            ratios = BodyRatios(
                shoulder_to_hip_ratio=shoulder_to_hip_ratio,
                waist_to_hip_ratio=waist_to_hip_ratio,
                shoulder_to_waist_ratio=shoulder_to_waist_ratio,
                torso_aspect_ratio=torso_aspect_ratio
            )
            
            logger.debug(f"Calculated ratios: {ratios}")
            return ratios
            
        except Exception as e:
            logger.error(f"Ratio calculation failed: {str(e)}")
            raise InsufficientKeypointsError(f"Failed to calculate ratios: {str(e)}")
    
    def _calculate_distance(self, point1: Tuple[float, float, float], point2: Tuple[float, float, float]) -> float:
        """Calculate Euclidean distance between two normalized points"""
        x1, y1, _ = point1
        x2, y2, _ = point2
        return np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    
    def _safe_divide(self, numerator: float, denominator: float, fallback: float) -> float:
        """Safe division with fallback value"""
        if denominator == 0 or not np.isfinite(denominator):
            logger.warning(f"Invalid denominator in ratio calculation: {denominator}, using fallback: {fallback}")
            return fallback
        
        result = numerator / denominator
        
        # Check for reasonable bounds
        if not np.isfinite(result) or result < 0:
            logger.warning(f"Invalid ratio result: {result}, using fallback: {fallback}")
            return fallback
            
        return result
    
    def validate_ratios(self, ratios: BodyRatios) -> bool:
        """Validate if calculated ratios are within expected ranges"""
        try:
            ratio_values = {
                'shoulder_to_hip_ratio': ratios.shoulder_to_hip_ratio,
                'waist_to_hip_ratio': ratios.waist_to_hip_ratio,
                'shoulder_to_waist_ratio': ratios.shoulder_to_waist_ratio,
                'torso_aspect_ratio': ratios.torso_aspect_ratio
            }
            
            for ratio_name, value in ratio_values.items():
                min_val, max_val = self.ratio_ranges[ratio_name]
                if not (min_val <= value <= max_val):
                    logger.warning(
                        f"Ratio {ratio_name} ({value:.3f}) outside expected range "
                        f"[{min_val}, {max_val}]"
                    )
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ratio validation failed: {str(e)}")
            return False
    
    def get_ratio_names(self) -> list[str]:
        """Get list of ratio names calculated by this service"""
        return list(self.ratio_ranges.keys())
    
    def get_ratio_ranges(self) -> Dict[str, Tuple[float, float]]:
        """Get expected ranges for each ratio"""
        return self.ratio_ranges.copy()
    
    def get_body_measurements_info(self) -> Dict[str, str]:
        """Get information about body measurements used in calculations"""
        return {
            'shoulder_width': 'Distance between left and right shoulder keypoints',
            'hip_width': 'Distance between left and right hip keypoints',
            'waist_width': 'Estimated as 75% of hip width (anatomical approximation)',
            'torso_height': 'Vertical distance from shoulder center to hip center'
        }
