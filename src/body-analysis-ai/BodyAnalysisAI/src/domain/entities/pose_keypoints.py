"""
Domain Entity - Pose Keypoints
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np


@dataclass
class PoseKeypoints:
    """Pose keypoints detected from image"""
    keypoints: Dict[str, Tuple[float, float, float]]  # name -> (x, y, confidence)
    image_dimensions: Tuple[int, int]  # (width, height)
    detection_confidence: float
    
    def get_keypoint(self, name: str) -> Optional[Tuple[float, float, float]]:
        """Get specific keypoint coordinates and confidence"""
        return self.keypoints.get(name)
    
    def is_keypoint_valid(self, name: str, min_confidence: float = 0.5) -> bool:
        """Check if keypoint meets confidence threshold"""
        keypoint = self.get_keypoint(name)
        return keypoint is not None and keypoint[2] >= min_confidence
    
    def get_valid_keypoints(self, min_confidence: float = 0.5) -> Dict[str, Tuple[float, float, float]]:
        """Get all keypoints above confidence threshold"""
        return {
            name: coords for name, coords in self.keypoints.items()
            if coords[2] >= min_confidence
        }
    
    def get_keypoint_names(self) -> List[str]:
        """Get list of available keypoint names"""
        return list(self.keypoints.keys())
    
    def calculate_distance(self, keypoint1: str, keypoint2: str) -> Optional[float]:
        """Calculate distance between two keypoints"""
        kp1 = self.get_keypoint(keypoint1)
        kp2 = self.get_keypoint(keypoint2)
        
        if kp1 is None or kp2 is None:
            return None
        
        return np.sqrt((kp1[0] - kp2[0])**2 + (kp1[1] - kp2[1])**2)
    
    def validate_required_keypoints(self, required_keypoints: List[str], min_confidence: float = 0.5) -> bool:
        """Validate that all required keypoints are present with sufficient confidence"""
        for keypoint in required_keypoints:
            if not self.is_keypoint_valid(keypoint, min_confidence):
                return False
        return True
