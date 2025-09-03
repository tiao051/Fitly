"""
Presentation DTOs - Public API
Clean imports for all data transfer objects
"""

# Body type and analysis DTOs
from .body_type_dto import BodyTypeResponse
from .body_ratios_dto import BodyRatiosDto

# Analysis request/response DTOs
from .analysis_dto import (
    AnalysisRequestDto,
    AnalysisResponseDto
)

# Validation DTOs
from .validation_dto import ValidationResponseDto

# History DTOs
from .history_dto import (
    AnalysisHistoryItemDto,
    AnalysisHistoryDto,
    TrendsResponseDto
)

# Common DTOs
from .common_dto import (
    HealthCheckResponseDto,
    ErrorResponseDto
)

# Public API exports
__all__ = [
    # Body type and ratios
    "BodyTypeResponse",
    "BodyRatiosDto",
    
    # Analysis
    "AnalysisRequestDto",
    "AnalysisResponseDto",
    
    # Validation
    "ValidationResponseDto",
    
    # History
    "AnalysisHistoryItemDto",
    "AnalysisHistoryDto", 
    "TrendsResponseDto",
    
    # Common
    "HealthCheckResponseDto",
    "ErrorResponseDto"
]
