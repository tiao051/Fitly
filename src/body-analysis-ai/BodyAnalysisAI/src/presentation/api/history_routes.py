"""
Presentation Layer - History API Routes
FastAPI routes for analysis history and trends
"""

from fastapi import APIRouter, HTTPException, Depends, Query
import logging
from typing import Optional

from ..dto import (
    AnalysisHistoryDto,
    TrendsResponseDto,
    ErrorResponseDto
)
from .dependencies import dependency_provider, DependencyProvider
from ...domain.entities import BodyAnalysisError

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/history", tags=["history"])


def get_dependency_provider() -> DependencyProvider:
    """FastAPI dependency to get provider"""
    return dependency_provider


@router.get("/{user_id}", response_model=AnalysisHistoryDto)
async def get_user_analysis_history(
    user_id: str,
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    provider: DependencyProvider = Depends(get_dependency_provider)
):
    """
    Get user's body analysis history
    
    - **user_id**: User identifier
    - **limit**: Maximum number of results to return (1-100)
    
    Returns:
        AnalysisHistoryDto containing user's analysis history
    """
    try:
        # Check if dependencies are ready
        if not provider.is_ready():
            await provider.initialize_dependencies()
        
        # Get use case and execute
        use_case = provider.get_history_use_case()
        history = await use_case.execute(user_id, limit)
        
        # Convert to DTO
        response = AnalysisHistoryDto(
            user_id=user_id,
            total_analyses=len(history),
            analyses=[
                {
                    "analysis_id": result.processing_metadata.get("analysis_id"),
                    "body_type": result.body_type.value,
                    "confidence_score": result.confidence_score,
                    "timestamp": result.processing_metadata.get("timestamp"),
                    "body_ratios": {
                        "shoulder_to_hip_ratio": result.body_ratios.shoulder_to_hip_ratio,
                        "waist_to_hip_ratio": result.body_ratios.waist_to_hip_ratio,
                        "shoulder_to_waist_ratio": result.body_ratios.shoulder_to_waist_ratio,
                        "torso_aspect_ratio": result.body_ratios.torso_aspect_ratio
                    }
                }
                for result in history
            ]
        )
        
        logger.info(f"Retrieved {len(history)} analyses for user {user_id}")
        return response
        
    except BodyAnalysisError as e:
        logger.error(f"History retrieval error: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error getting history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{user_id}/trends", response_model=TrendsResponseDto)
async def get_user_analysis_trends(
    user_id: str,
    days_back: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    provider: DependencyProvider = Depends(get_dependency_provider)
):
    """
    Get user's body analysis trends and statistics
    
    - **user_id**: User identifier
    - **days_back**: Number of days to look back for trend analysis (1-365)
    
    Returns:
        TrendsResponseDto containing trend analysis
    """
    try:
        # Check if dependencies are ready
        if not provider.is_ready():
            await provider.initialize_dependencies()
        
        # Get service and execute
        service = provider.get_aggregation_service()
        trends_data = await service.get_analysis_trends(user_id, days_back)
        
        # Convert to DTO
        response = TrendsResponseDto(
            user_id=user_id,
            analysis_period_days=days_back,
            trends=trends_data.get("trends", {}),
            message=trends_data.get("message", "Trends calculated successfully")
        )
        
        logger.info(f"Generated trends for user {user_id} over {days_back} days")
        return response
        
    except BodyAnalysisError as e:
        logger.error(f"Trends calculation error: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error calculating trends: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
