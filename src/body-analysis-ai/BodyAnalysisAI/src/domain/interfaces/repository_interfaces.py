"""
Domain Interfaces - Data Persistence
Contracts for data storage and retrieval services
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime

from ..entities import BodyAnalysisResult


class IAnalysisRepository(ABC):
    """Interface for analysis result persistence"""
    
    @abstractmethod
    async def save_analysis(self, result: BodyAnalysisResult) -> str:
        """
        Save analysis result to storage
        
        Args:
            result: Analysis result to save
            
        Returns:
            Unique identifier for the saved analysis
        """
        pass
    
    @abstractmethod
    async def get_analysis(self, analysis_id: str) -> Optional[BodyAnalysisResult]:
        """
        Retrieve analysis result by ID
        
        Args:
            analysis_id: Unique identifier of the analysis
            
        Returns:
            BodyAnalysisResult if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_user_analyses(
        self, 
        user_id: str, 
        limit: int = 50,
        offset: int = 0
    ) -> List[BodyAnalysisResult]:
        """
        Get analysis history for a user
        
        Args:
            user_id: User identifier
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of analysis results for the user
        """
        pass
    
    @abstractmethod
    async def get_analyses_by_date_range(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[BodyAnalysisResult]:
        """
        Get analyses within a date range
        
        Args:
            user_id: User identifier
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            List of analysis results in the date range
        """
        pass
    
    @abstractmethod
    async def delete_analysis(self, analysis_id: str) -> bool:
        """
        Delete an analysis result
        
        Args:
            analysis_id: Unique identifier of the analysis
            
        Returns:
            True if deleted successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_analysis_count(self, user_id: str) -> int:
        """
        Get total number of analyses for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Total count of analyses for the user
        """
        pass


class IImageRepository(ABC):
    """Interface for image storage and retrieval"""
    
    @abstractmethod
    async def save_image(
        self, 
        image_data: bytes, 
        content_type: str,
        user_id: str
    ) -> str:
        """
        Save image to storage
        
        Args:
            image_data: Raw image bytes
            content_type: MIME type of the image
            user_id: User who uploaded the image
            
        Returns:
            Unique identifier for the stored image
        """
        pass
    
    @abstractmethod
    async def get_image(self, image_id: str) -> Optional[bytes]:
        """
        Retrieve image by ID
        
        Args:
            image_id: Unique identifier of the image
            
        Returns:
            Image bytes if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def delete_image(self, image_id: str) -> bool:
        """
        Delete an image from storage
        
        Args:
            image_id: Unique identifier of the image
            
        Returns:
            True if deleted successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_image_metadata(self, image_id: str) -> Optional[dict]:
        """
        Get metadata for an image
        
        Args:
            image_id: Unique identifier of the image
            
        Returns:
            Dictionary with image metadata if found, None otherwise
        """
        pass
