"""
Domain Entity - Body Ratios and Measurements
"""

from dataclasses import dataclass
import numpy as np


@dataclass
class BodyRatios:
    """Body measurement ratios extracted from pose"""
    shoulder_to_hip_ratio: float
    waist_to_hip_ratio: float
    shoulder_to_waist_ratio: float
    torso_aspect_ratio: float
    
    def to_feature_vector(self) -> np.ndarray:
        """Convert ratios to feature vector for ML"""
        return np.array([
            self.shoulder_to_hip_ratio,
            self.waist_to_hip_ratio,
            self.shoulder_to_waist_ratio,
            self.torso_aspect_ratio
        ])
    
    def validate_ratios(self) -> bool:
        """Validate that ratios are within reasonable bounds"""
        ratios = [
            self.shoulder_to_hip_ratio,
            self.waist_to_hip_ratio,
            self.shoulder_to_waist_ratio,
            self.torso_aspect_ratio
        ]
        
        # Check for valid positive values and reasonable bounds
        for ratio in ratios:
            if ratio <= 0 or ratio > 5.0:  # Reasonable upper bound
                return False
        
        return True
    
    def get_ratio_description(self) -> dict:
        """Get human-readable description of ratios"""
        return {
            "shoulder_to_hip": f"{self.shoulder_to_hip_ratio:.2f}",
            "waist_to_hip": f"{self.waist_to_hip_ratio:.2f}",
            "shoulder_to_waist": f"{self.shoulder_to_waist_ratio:.2f}",
            "torso_aspect": f"{self.torso_aspect_ratio:.2f}"
        }
