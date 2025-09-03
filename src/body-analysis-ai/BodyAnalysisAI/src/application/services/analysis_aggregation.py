"""
Application Service - Analysis Aggregation
Service for aggregating and analyzing user data trends
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import Counter

from ...domain.entities import BodyAnalysisResult
from ...domain.interfaces import IAnalysisRepository

logger = logging.getLogger(__name__)


class AnalysisAggregationService:
    """Service for aggregating and analyzing user data"""
    
    def __init__(self, repository: IAnalysisRepository):
        self.repository = repository
    
    async def get_analysis_trends(self, user_id: str, days_back: int = 30) -> Dict[str, Any]:
        """
        Analyze user's body analysis trends over time
        
        Args:
            user_id: User identifier
            days_back: Number of days to look back for trend analysis
            
        Returns:
            Dictionary containing trend analysis data
        """
        try:
            # Get user's analysis history
            history = await self.repository.get_user_history(user_id, limit=100)
            
            if not history:
                return {"message": "No analysis history found", "trends": {}}
            
            # Filter by date range if needed
            cutoff_date = datetime.now() - timedelta(days=days_back)
            recent_history = [
                result for result in history
                if self._parse_timestamp(result.processing_metadata.get("timestamp")) >= cutoff_date
            ]
            
            if not recent_history:
                recent_history = history  # Fallback to all history
            
            # Calculate trends
            trends = self._calculate_trends(recent_history)
            trends["analysis_period_days"] = days_back
            trends["oldest_analysis"] = history[0].processing_metadata.get("timestamp") if history else None
            trends["most_recent_analysis"] = history[-1].processing_metadata.get("timestamp") if history else None
            
            logger.info(f"Generated trends for user {user_id}: {len(recent_history)} analyses")
            return {"trends": trends, "message": "Trends calculated successfully"}
            
        except Exception as e:
            logger.error(f"Failed to get trends for user {user_id}: {str(e)}")
            raise
    
    async def get_global_statistics(self) -> Dict[str, Any]:
        """
        Get global statistics across all users
        
        Returns:
            Dictionary containing global analytics
        """
        try:
            # This would typically query aggregate data from the repository
            # For now, return placeholder structure
            stats = {
                "total_analyses": 0,
                "unique_users": 0,
                "body_type_distribution": {},
                "average_confidence": 0.0,
                "most_active_day": None,
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info("Generated global statistics")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get global statistics: {str(e)}")
            raise
    
    def _calculate_trends(self, history: List[BodyAnalysisResult]) -> Dict[str, Any]:
        """Calculate various trend metrics from analysis history"""
        body_types = [result.body_type.value for result in history]
        confidence_scores = [result.confidence_score for result in history]
        
        # Body type analysis
        body_type_counts = Counter(body_types)
        most_common_type = body_type_counts.most_common(1)[0] if body_type_counts else ("unknown", 0)
        
        # Confidence analysis
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        min_confidence = min(confidence_scores) if confidence_scores else 0.0
        max_confidence = max(confidence_scores) if confidence_scores else 0.0
        
        # Consistency analysis
        consistency_score = self._calculate_consistency(body_types)
        
        # Temporal analysis
        temporal_trends = self._analyze_temporal_patterns(history)
        
        return {
            "total_analyses": len(history),
            "body_type_distribution": dict(body_type_counts),
            "most_common_body_type": most_common_type[0],
            "most_common_type_count": most_common_type[1],
            "confidence_metrics": {
                "average": round(avg_confidence, 3),
                "minimum": round(min_confidence, 3),
                "maximum": round(max_confidence, 3)
            },
            "consistency_score": round(consistency_score, 3),
            "recent_body_type": history[-1].body_type.value if history else None,
            "temporal_patterns": temporal_trends
        }
    
    def _calculate_consistency(self, body_types: List[str]) -> float:
        """Calculate consistency of body type classifications"""
        if not body_types:
            return 0.0
        
        # Calculate percentage of most common type
        type_counts = Counter(body_types)
        most_common_count = type_counts.most_common(1)[0][1]
        
        return most_common_count / len(body_types)
    
    def _analyze_temporal_patterns(self, history: List[BodyAnalysisResult]) -> Dict[str, Any]:
        """Analyze temporal patterns in the analysis history"""
        patterns = {
            "frequency": "unknown",
            "trend_direction": "stable",
            "confidence_trend": "stable"
        }
        
        try:
            if len(history) < 2:
                return patterns
            
            # Simple frequency analysis
            if len(history) >= 7:
                patterns["frequency"] = "high"  # 7+ analyses
            elif len(history) >= 3:
                patterns["frequency"] = "medium"  # 3-6 analyses  
            else:
                patterns["frequency"] = "low"  # 1-2 analyses
            
            # Confidence trend (simple comparison of first half vs second half)
            mid_point = len(history) // 2
            first_half_confidence = sum(r.confidence_score for r in history[:mid_point]) / mid_point
            second_half_confidence = sum(r.confidence_score for r in history[mid_point:]) / (len(history) - mid_point)
            
            confidence_diff = second_half_confidence - first_half_confidence
            if confidence_diff > 0.05:
                patterns["confidence_trend"] = "improving"
            elif confidence_diff < -0.05:
                patterns["confidence_trend"] = "declining"
            
        except Exception as e:
            logger.warning(f"Error analyzing temporal patterns: {str(e)}")
        
        return patterns
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string to datetime object"""
        try:
            if timestamp_str:
                return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except Exception:
            pass
        
        # Fallback to current time if parsing fails
        return datetime.now()
