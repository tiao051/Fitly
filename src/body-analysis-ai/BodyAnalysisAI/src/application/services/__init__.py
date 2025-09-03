"""
Application Services - Business Logic Coordination
"""

import logging
from typing import Optional, Dict, Any

from ...domain.entities import BodyAnalysisResult
from ...domain.interfaces import IAnalysisRepository

logger = logging.getLogger(__name__)


class AnalysisAggregationService:
    """Service for aggregating and analyzing user data"""
    
    def __init__(self, repository: IAnalysisRepository):
        self.repository = repository
    
    async def get_analysis_trends(self, user_id: str) -> Dict[str, Any]:
        """Analyze user's body analysis trends over time"""
        try:
            history = await self.repository.get_user_history(user_id, limit=50)
            
            if not history:
                return {"message": "No analysis history found"}
            
            # Analyze trends
            body_types = [result.body_type.value for result in history]
            confidence_scores = [result.confidence_score for result in history]
            
            trends = {
                "total_analyses": len(history),
                "most_common_body_type": max(set(body_types), key=body_types.count),
                "average_confidence": sum(confidence_scores) / len(confidence_scores),
                "recent_body_type": history[-1].body_type.value,
                "consistency_score": self._calculate_consistency(body_types)
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to get trends for user {user_id}: {str(e)}")
            raise
    
    def _calculate_consistency(self, body_types: list[str]) -> float:
        """Calculate consistency of body type classifications"""
        if not body_types:
            return 0.0
        
        most_common = max(set(body_types), key=body_types.count)
        consistency = body_types.count(most_common) / len(body_types)
        return round(consistency, 3)


class ModelPerformanceService:
    """Service for monitoring model performance"""
    
    def __init__(self, repository: IAnalysisRepository):
        self.repository = repository
    
    async def get_model_metrics(self) -> Dict[str, Any]:
        """Get aggregated model performance metrics"""
        # This would typically pull from a larger dataset
        # For now, return basic metrics structure
        return {
            "total_analyses": 0,
            "average_confidence": 0.0,
            "body_type_distribution": {},
            "low_confidence_rate": 0.0
        }
