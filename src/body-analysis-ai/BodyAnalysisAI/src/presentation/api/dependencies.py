"""
Presentation Layer - Dependency Provider
Handles dependency injection for the API layer
"""

import logging
from typing import Optional

from ...application.use_cases import (
    AnalyzeBodyTypeUseCase,
    GetAnalysisHistoryUseCase,
    ValidateImageUseCase
)
from ...application.services import AnalysisAggregationService
from ...infrastructure.ml_models import YOLOPoseExtractor, SVMHybridClassifier, BodyRatioCalculator, ImageProcessor, MLModelManager
# from ...infrastructure.ml_models import ResNetFeatureExtractor  # Temporarily disabled
from ...infrastructure.repositories import InMemoryAnalysisRepository
from ...domain.interfaces import (
    IPoseExtractor,
    IRatioCalculator,
    IDLFeatureExtractor,
    IHybridClassifier,
    IAnalysisRepository,
    IImageProcessor
)

logger = logging.getLogger(__name__)


class DependencyProvider:
    """
    Dependency injection provider for the API layer
    
    This class is responsible for creating and managing all dependencies
    required by the application use cases and services.
    """
    
    def __init__(self):
        self._analyze_use_case: Optional[AnalyzeBodyTypeUseCase] = None
        self._history_use_case: Optional[GetAnalysisHistoryUseCase] = None
        self._validation_use_case: Optional[ValidateImageUseCase] = None
        self._aggregation_service: Optional[AnalysisAggregationService] = None
        self._models_loaded = {
            "pose_extractor": False, 
            "dl_extractor": False, 
            "classifier": False
        }
        self._dependencies_initialized = False
    
    async def initialize_dependencies(self):
        """Initialize all dependencies if not already done"""
        if self._dependencies_initialized:
            return
        
        try:
            logger.info("Initializing dependencies...")
            
            # Initialize infrastructure components
            repository = InMemoryAnalysisRepository()
            
            # Initialize ML models (placeholder - would load actual models)
            pose_extractor = YOLOPoseExtractor()
            ratio_calculator = self._create_ratio_calculator()
            # dl_feature_extractor = ResNetFeatureExtractor()  # Temporarily disabled
            dl_feature_extractor = None  # Placeholder
            hybrid_classifier = SVMHybridClassifier()
            image_processor = self._create_image_processor()
            
            # Update model loading status
            self._models_loaded["pose_extractor"] = pose_extractor.is_model_loaded()
            # self._models_loaded["dl_extractor"] = dl_feature_extractor.is_model_loaded()  # Temporarily disabled
            self._models_loaded["dl_extractor"] = False  # Placeholder
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
            
            self._dependencies_initialized = True
            logger.info("Dependencies initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize dependencies: {str(e)}")
            raise
    
    def get_analyze_use_case(self) -> AnalyzeBodyTypeUseCase:
        """Get body analysis use case"""
        if not self._analyze_use_case:
            raise RuntimeError("Dependencies not initialized. Call initialize_dependencies() first.")
        return self._analyze_use_case
    
    def get_history_use_case(self) -> GetAnalysisHistoryUseCase:
        """Get analysis history use case"""
        if not self._history_use_case:
            raise RuntimeError("Dependencies not initialized. Call initialize_dependencies() first.")
        return self._history_use_case
    
    def get_validation_use_case(self) -> ValidateImageUseCase:
        """Get image validation use case"""
        if not self._validation_use_case:
            raise RuntimeError("Dependencies not initialized. Call initialize_dependencies() first.")
        return self._validation_use_case
    
    def get_aggregation_service(self) -> AnalysisAggregationService:
        """Get analysis aggregation service"""
        if not self._aggregation_service:
            raise RuntimeError("Dependencies not initialized. Call initialize_dependencies() first.")
        return self._aggregation_service
    
    def get_model_status(self) -> dict:
        """Get current model loading status"""
        return self._models_loaded.copy()
    
    def is_ready(self) -> bool:
        """Check if all dependencies are ready"""
        return (self._dependencies_initialized and 
                all(self._models_loaded.values()))
    
    def _create_ratio_calculator(self):
        """Create ratio calculator instance"""
        # Placeholder - would create actual implementation
        return BodyRatioCalculator()
    
    def _create_image_processor(self):
        """Create image processor instance"""
        # Placeholder - would create actual implementation
        return ImageProcessor()


# Global dependency provider instance
dependency_provider = DependencyProvider()
