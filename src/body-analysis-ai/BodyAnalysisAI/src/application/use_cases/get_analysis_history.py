"""
Application Use Case - Get Analysis History
Retrieve user's body analysis history
"""

from typing import List
import logging

from ...domain.entities import BodyAnalysisResult, BodyAnalysisError
from ...domain.interfaces import IAnalysisRepository

logger = logging.getLogger(__name__)


class GetAnalysisHistoryUseCase:
    """Use case for retrieving user's analysis history"""
    
    def __init__(self, analysis_repository: IAnalysisRepository):
        self.analysis_repository = analysis_repository
    
    async def execute(self, user_id: str, limit: int = 10) -> List[BodyAnalysisResult]:
        """
        Get user's analysis history
        
        Args:
            user_id: User identifier
            limit: Maximum number of results to return
            
        Returns:
            List of BodyAnalysisResult ordered by most recent first
            
        Raises:
            BodyAnalysisError: If retrieval fails
        """
        try:
            if not user_id:
                raise ValueError("User ID is required")
            
            if limit <= 0:
                raise ValueError("Limit must be positive")
                
            history = await self.analysis_repository.get_user_history(user_id, limit)
            logger.info(f"Retrieved {len(history)} results for user {user_id}")
            
            return history
            
        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Failed to get history for user {user_id}: {str(e)}")
            raise BodyAnalysisError(f"Failed to retrieve history: {str(e)}") from e
