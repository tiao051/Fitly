"""
Presentation Layer - API Endpoints
FastAPI routes for body analysis service
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
import numpy as np
import cv2
from PIL import Image
import io
import logging
import time
from typing import Optional

from ..dto import (
    AnalysisResponseDto,
    AnalysisHistoryDto,
    ValidationResponseDto,
    TrendsResponseDto,
    HealthCheckResponseDto,
    ErrorResponseDto,
    BodyRatiosDto
)
from ...application.use_cases import (
    AnalyzeBodyTypeUseCase,
    GetAnalysisHistoryUseCase,
    ValidateImageUseCase
)
from ...application.services import AnalysisAggregationService
from ...domain.entities import BodyAnalysisError, InsufficientKeypointsError, ModelLoadError

logger = logging.getLogger(__name__)

# Global variables to track service state
SERVICE_START_TIME = time.time()


class DependencyProvider:
    """Dependency injection provider"""
    
    def __init__(self):
        self._analyze_use_case: Optional[AnalyzeBodyTypeUseCase] = None
        self._history_use_case: Optional[GetAnalysisHistoryUseCase] = None
        self._validation_use_case: Optional[ValidateImageUseCase] = None
        self._aggregation_service: Optional[AnalysisAggregationService] = None
        self._models_loaded = {"pose_extractor": False, "dl_extractor": False, "classifier": False}
    
    def get_analyze_use_case(self) -> AnalyzeBodyTypeUseCase:
        """Get body analysis use case"""
        if self._analyze_use_case is None:
            self._initialize_dependencies()
        return self._analyze_use_case
    
    def get_history_use_case(self) -> GetAnalysisHistoryUseCase:
        """Get history use case"""
        if self._history_use_case is None:
            self._initialize_dependencies()
        return self._history_use_case
    
    def get_validation_use_case(self) -> ValidateImageUseCase:
        """Get validation use case"""
        if self._validation_use_case is None:
            self._initialize_dependencies()
        return self._validation_use_case
    
    def get_aggregation_service(self) -> AnalysisAggregationService:
        """Get aggregation service"""
        if self._aggregation_service is None:
            self._initialize_dependencies()
        return self._aggregation_service
    
    def get_models_status(self) -> dict:
        """Get model loading status"""
        return self._models_loaded.copy()
    
    def _initialize_dependencies(self):
        """Initialize all dependencies"""
        try:
            from ...infrastructure.ml_models import (
                YOLOPoseExtractor,
                BodyRatioCalculator,
                ResNetFeatureExtractor,
                SVMHybridClassifier,
                ImageProcessor
            )
            from ...infrastructure.repositories import InMemoryAnalysisRepository
            
            # Initialize infrastructure components
            image_processor = ImageProcessor()
            pose_extractor = YOLOPoseExtractor()
            ratio_calculator = BodyRatioCalculator()
            dl_feature_extractor = ResNetFeatureExtractor()
            hybrid_classifier = SVMHybridClassifier()
            repository = InMemoryAnalysisRepository()
            
            # Track model loading status
            self._models_loaded["pose_extractor"] = True
            self._models_loaded["dl_extractor"] = True
            self._models_loaded["classifier"] = hybrid_classifier.is_model_loaded()
            
            # Initialize use cases
            self._analyze_use_case = AnalyzeBodyTypeUseCase(
                image_processor=image_processor,
                pose_extractor=pose_extractor,
                ratio_calculator=ratio_calculator,
                dl_feature_extractor=dl_feature_extractor,
                hybrid_classifier=hybrid_classifier,
                analysis_repository=repository
            )
            
            self._history_use_case = GetAnalysisHistoryUseCase(repository)
            self._validation_use_case = ValidateImageUseCase(image_processor)
            self._aggregation_service = AnalysisAggregationService(repository)
            
            logger.info("Dependencies initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize dependencies: {str(e)}")
            raise


# Global dependency provider
dependency_provider = DependencyProvider()

# Create router
router = APIRouter()


def get_dependency_provider() -> DependencyProvider:
    """FastAPI dependency to get provider"""
    return dependency_provider


async def convert_upload_to_numpy(file: UploadFile) -> np.ndarray:
    """Convert uploaded file to numpy array"""
    try:
        # Read file contents
        contents = await file.read()
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(contents))
        
        # Convert to numpy array
        image_array = np.array(image)
        
        # Ensure proper format
        if len(image_array.shape) == 3:
            if image_array.shape[2] == 4:  # RGBA
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGBA2RGB)
            elif image_array.shape[2] == 3:  # RGB
                pass  # Keep as is
        
        return image_array
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")


@router.post("/analyze", response_model=AnalysisResponseDto)
async def analyze_body_type(
    file: UploadFile = File(..., description="Body image for analysis"),
    user_id: Optional[str] = Form(None, description="Optional user identifier"),
    save_result: bool = Form(True, description="Whether to save the result"),
    provider: DependencyProvider = Depends(get_dependency_provider)
):
    """
    Analyze body type from uploaded image using hybrid DL+ML approach
    
    - **file**: Image file (JPEG, PNG) showing full torso
    - **user_id**: Optional user identifier for tracking
    - **save_result**: Whether to save the analysis result
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Convert to numpy array
        image = await convert_upload_to_numpy(file)
        
        # Get use case and execute analysis
        use_case = provider.get_analyze_use_case()
        result = await use_case.execute(image, user_id, save_result)
        
        # Convert to DTO
        response = AnalysisResponseDto(
            body_type=result.body_type.value,
            confidence_score=result.confidence_score,
            body_ratios=BodyRatiosDto(
                shoulder_to_hip_ratio=result.body_ratios.shoulder_to_hip_ratio,
                waist_to_hip_ratio=result.body_ratios.waist_to_hip_ratio,
                shoulder_to_waist_ratio=result.body_ratios.shoulder_to_waist_ratio,
                torso_aspect_ratio=result.body_ratios.torso_aspect_ratio
            ),
            keypoints_detected=len(result.pose_keypoints.keypoints),
            detection_confidence=result.pose_keypoints.detection_confidence,
            processing_metadata=result.processing_metadata,
            result_id=result.processing_metadata.get("result_id")
        )
        
        return response
        
    except InsufficientKeypointsError as e:
        raise HTTPException(status_code=422, detail=f"Insufficient keypoints detected: {str(e)}")
    except ModelLoadError as e:
        raise HTTPException(status_code=503, detail=f"Model loading error: {str(e)}")
    except BodyAnalysisError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/validate", response_model=ValidationResponseDto)
async def validate_image(
    file: UploadFile = File(..., description="Image to validate"),
    provider: DependencyProvider = Depends(get_dependency_provider)
):
    """
    Validate image quality and format before analysis
    
    - **file**: Image file to validate
    """
    try:
        # Convert to numpy array
        image = await convert_upload_to_numpy(file)
        
        # Get use case and validate
        use_case = provider.get_validation_use_case()
        validation_result = use_case.execute(image)
        
        return ValidationResponseDto(
            is_valid=validation_result["is_valid"],
            image_shape=list(validation_result["image_shape"]),
            image_dtype=validation_result["image_dtype"],
            recommendations=validation_result["recommendations"]
        )
        
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get("/history/{user_id}", response_model=AnalysisHistoryDto)
async def get_analysis_history(
    user_id: str,
    limit: int = 10,
    provider: DependencyProvider = Depends(get_dependency_provider)
):
    """
    Get user's body analysis history
    
    - **user_id**: User identifier
    - **limit**: Maximum number of results (default: 10)
    """
    try:
        use_case = provider.get_history_use_case()
        results = await use_case.execute(user_id, limit)
        
        # Convert results to DTOs
        result_dtos = []
        for result in results:
            dto = AnalysisResponseDto(
                body_type=result.body_type.value,
                confidence_score=result.confidence_score,
                body_ratios=BodyRatiosDto(
                    shoulder_to_hip_ratio=result.body_ratios.shoulder_to_hip_ratio,
                    waist_to_hip_ratio=result.body_ratios.waist_to_hip_ratio,
                    shoulder_to_waist_ratio=result.body_ratios.shoulder_to_waist_ratio,
                    torso_aspect_ratio=result.body_ratios.torso_aspect_ratio
                ),
                keypoints_detected=len(result.pose_keypoints.keypoints),
                detection_confidence=result.pose_keypoints.detection_confidence,
                processing_metadata=result.processing_metadata,
                result_id=result.processing_metadata.get("result_id")
            )
            result_dtos.append(dto)
        
        return AnalysisHistoryDto(
            total_results=len(result_dtos),
            results=result_dtos
        )
        
    except Exception as e:
        logger.error(f"Failed to get history for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")


@router.get("/trends/{user_id}", response_model=TrendsResponseDto)
async def get_analysis_trends(
    user_id: str,
    provider: DependencyProvider = Depends(get_dependency_provider)
):
    """
    Get user's body analysis trends and statistics
    
    - **user_id**: User identifier
    """
    try:
        service = provider.get_aggregation_service()
        trends = await service.get_analysis_trends(user_id)
        
        if "message" in trends:
            raise HTTPException(status_code=404, detail=trends["message"])
        
        return TrendsResponseDto(**trends)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get trends for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve trends: {str(e)}")


@router.get("/health", response_model=HealthCheckResponseDto)
async def health_check(
    provider: DependencyProvider = Depends(get_dependency_provider)
):
    """
    Health check endpoint with model status
    """
    try:
        uptime = time.time() - SERVICE_START_TIME
        models_status = provider.get_models_status()
        
        return HealthCheckResponseDto(
            status="healthy",
            version="2.0.0",
            models_loaded=models_status,
            uptime_seconds=uptime
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthCheckResponseDto(
            status="unhealthy",
            version="2.0.0",
            models_loaded={"error": str(e)},
            uptime_seconds=time.time() - SERVICE_START_TIME
        )
