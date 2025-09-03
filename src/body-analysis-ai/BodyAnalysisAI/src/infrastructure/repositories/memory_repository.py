"""
Infrastructure - In-Memory Analysis Repository
In-memory storage implementation for development and testing
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict
import logging

from ...domain.entities import BodyAnalysisResult
from ...domain.interfaces import IAnalysisRepository

logger = logging.getLogger(__name__)


class InMemoryAnalysisRepository(IAnalysisRepository):
    """In-memory repository implementation for development and testing"""
    
    def __init__(self):
        self.analyses: Dict[str, BodyAnalysisResult] = {}
        self.user_analyses: Dict[str, List[str]] = {}  # user_id -> list of analysis_ids
    
    async def save_analysis(self, result: BodyAnalysisResult) -> str:
        """Save analysis result and return unique identifier"""
        analysis_id = str(uuid.uuid4())
        
        # Add timestamps and ID to result
        result.processing_metadata["analysis_id"] = analysis_id
        result.processing_metadata["created_at"] = datetime.utcnow().isoformat()
        result.processing_metadata["updated_at"] = datetime.utcnow().isoformat()
        
        # Store the analysis
        self.analyses[analysis_id] = result
        
        # Track user associations if user_id is in metadata
        user_id = result.processing_metadata.get("user_id")
        if user_id:
            if user_id not in self.user_analyses:
                self.user_analyses[user_id] = []
            self.user_analyses[user_id].append(analysis_id)
        
        logger.debug(f"Saved analysis {analysis_id} to in-memory storage")
        return analysis_id
    
    async def get_analysis(self, analysis_id: str) -> Optional[BodyAnalysisResult]:
        """Retrieve analysis result by ID"""
        result = self.analyses.get(analysis_id)
        if result:
            logger.debug(f"Retrieved analysis {analysis_id} from in-memory storage")
        else:
            logger.warning(f"Analysis {analysis_id} not found in storage")
        return result
    
    async def get_user_analyses(
        self, 
        user_id: str, 
        limit: int = 50,
        offset: int = 0
    ) -> List[BodyAnalysisResult]:
        """Get analysis history for a user"""
        analysis_ids = self.user_analyses.get(user_id, [])
        
        # Apply pagination
        start_idx = offset
        end_idx = min(start_idx + limit, len(analysis_ids))
        paginated_ids = analysis_ids[start_idx:end_idx]
        
        # Retrieve analyses
        results = []
        for analysis_id in paginated_ids:
            analysis = self.analyses.get(analysis_id)
            if analysis:
                results.append(analysis)
        
        # Sort by creation time (most recent first)
        results.sort(
            key=lambda x: x.processing_metadata.get("created_at", ""),
            reverse=True
        )
        
        logger.debug(f"Retrieved {len(results)} analyses for user {user_id}")
        return results
    
    async def get_analyses_by_date_range(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[BodyAnalysisResult]:
        """Get analyses within a date range"""
        all_user_analyses = await self.get_user_analyses(user_id, limit=1000)
        
        filtered_analyses = []
        for analysis in all_user_analyses:
            created_at_str = analysis.processing_metadata.get("created_at")
            if created_at_str:
                try:
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    if start_date <= created_at <= end_date:
                        filtered_analyses.append(analysis)
                except ValueError:
                    logger.warning(f"Invalid date format in analysis metadata: {created_at_str}")
        
        logger.debug(f"Retrieved {len(filtered_analyses)} analyses for user {user_id} in date range")
        return filtered_analyses
    
    async def delete_analysis(self, analysis_id: str) -> bool:
        """Delete an analysis result"""
        if analysis_id in self.analyses:
            # Get analysis to find user_id for cleanup
            analysis = self.analyses[analysis_id]
            user_id = analysis.processing_metadata.get("user_id")
            
            # Remove from main storage
            del self.analyses[analysis_id]
            
            # Remove from user tracking
            if user_id and user_id in self.user_analyses:
                try:
                    self.user_analyses[user_id].remove(analysis_id)
                except ValueError:
                    pass  # Analysis ID not in user list
            
            logger.debug(f"Deleted analysis {analysis_id} from in-memory storage")
            return True
        
        logger.warning(f"Analysis {analysis_id} not found for deletion")
        return False
    
    async def get_analysis_count(self, user_id: str) -> int:
        """Get total number of analyses for a user"""
        count = len(self.user_analyses.get(user_id, []))
        logger.debug(f"User {user_id} has {count} analyses")
        return count
    
    def clear_all_data(self):
        """Clear all stored data (for testing purposes)"""
        self.analyses.clear()
        self.user_analyses.clear()
        logger.info("Cleared all in-memory analysis data")
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        total_analyses = len(self.analyses)
        total_users = len(self.user_analyses)
        
        user_analysis_counts = {
            user_id: len(analysis_ids) 
            for user_id, analysis_ids in self.user_analyses.items()
        }
        
        return {
            'total_analyses': total_analyses,
            'total_users': total_users,
            'analyses_per_user': user_analysis_counts,
            'storage_type': 'in_memory'
        }
