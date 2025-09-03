"""
Domain Interface - Ratio Calculation
Contract for body ratio calculation services
"""

from abc import ABC, abstractmethod

from ..entities import PoseKeypoints, BodyRatios


class IRatioCalculator(ABC):
    """Interface for body ratio calculations"""
    
    @abstractmethod
    def calculate_ratios(self, keypoints: PoseKeypoints) -> BodyRatios:
        """
        Calculate body proportions from pose keypoints
        
        Args:
            keypoints: Extracted pose keypoints
            
        Returns:
            BodyRatios object with calculated proportions
        """
        pass
    
    @abstractmethod
    def validate_ratios(self, ratios: BodyRatios) -> bool:
        """
        Validate if calculated ratios are within expected ranges
        
        Args:
            ratios: Calculated body ratios
            
        Returns:
            True if ratios are valid and reasonable
        """
        pass
    
    @abstractmethod
    def get_ratio_names(self) -> list[str]:
        """Get list of ratio names calculated by this service"""
        pass
    
    @abstractmethod
    def get_ratio_ranges(self) -> dict[str, tuple[float, float]]:
        """
        Get expected ranges for each ratio
        
        Returns:
            Dictionary mapping ratio names to (min, max) tuples
        """
        pass
