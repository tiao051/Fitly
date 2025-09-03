"""
Application Layer - Use Cases
Contains business logic orchestration
"""

from typing import Optional, Dict, Any
import numpy as np
import logging

from ...domain.entities import (
    BodyAnalysisResult, 
    HybridFeatures, 
    BodyAnalysisError, 
    InsufficientKeypointsError
)
from ...domain.interfaces import (
    IPoseExtractor,
    IRatioCalculator, 
    IDLFeatureExtractor,
    IHybridClassifier,
    IAnalysisRepository,
    IImageProcessor
)

logger = logging.getLogger(__name__)


class AnalyzeBodyTypeUseCase:
    """
    Main use case for body type analysis using hybrid approach
    """
    
    def __init__(
        self,
        image_processor: IImageProcessor,
        pose_extractor: IPoseExtractor,
        ratio_calculator: IRatioCalculator,
        dl_feature_extractor: IDLFeatureExtractor,
        hybrid_classifier: IHybridClassifier,
        analysis_repository: Optional[IAnalysisRepository] = None
    ):
        self.image_processor = image_processor
        self.pose_extractor = pose_extractor
        self.ratio_calculator = ratio_calculator
        self.dl_feature_extractor = dl_feature_extractor
        self.hybrid_classifier = hybrid_classifier
        self.analysis_repository = analysis_repository
    
    async def execute(
        self, 
        image: np.ndarray, 
        user_id: Optional[str] = None,
        save_result: bool = True
    ) -> BodyAnalysisResult:
        """
        Execute the complete body analysis workflow
        
        Steps:
        1. Preprocess and validate image
        2. Extract pose keypoints
        3. Calculate body ratios
        4. Extract DL embeddings
        5. Combine features and classify
        6. Save result (optional)
        """
        try:
            # Step 1: Preprocess and validate image
            if not self.image_processor.validate_image(image):
                raise BodyAnalysisError("Invalid image format or quality")
            
            processed_image = self.image_processor.preprocess_image(image)
            logger.info("Image preprocessed successfully")
            
            # Step 2: Extract pose keypoints
            pose_keypoints = await self.pose_extractor.extract_keypoints(processed_image)
            if not pose_keypoints:
                raise InsufficientKeypointsError("Failed to extract pose keypoints")
            
            if not self.pose_extractor.validate_keypoints(pose_keypoints):
                raise InsufficientKeypointsError("Insufficient keypoints for analysis")
            
            logger.info(f"Extracted {len(pose_keypoints.keypoints)} pose keypoints")
            
            # Step 3: Calculate body ratios
            body_ratios = self.ratio_calculator.calculate_ratios(pose_keypoints)
            logger.info("Body ratios calculated")
            
            # Step 4: Extract DL embeddings
            dl_embeddings = await self.dl_feature_extractor.extract_embeddings(processed_image)
            logger.info(f"DL embeddings extracted: {dl_embeddings.embedding_dimension}D")
            
            # Step 5: Combine features and classify
            hybrid_features = HybridFeatures(
                dl_embeddings=dl_embeddings,
                body_ratios=body_ratios
            )
            
            body_type, confidence = await self.hybrid_classifier.classify(hybrid_features)
            logger.info(f"Classification result: {body_type.value} (confidence: {confidence:.3f})")
            
            # Step 6: Create result
            result = BodyAnalysisResult(
                body_type=body_type,
                confidence_score=confidence,
                pose_keypoints=pose_keypoints,
                body_ratios=body_ratios,
                dl_embeddings=dl_embeddings,
                processing_metadata={
                    "image_shape": processed_image.shape,
                    "keypoints_count": len(pose_keypoints.keypoints),
                    "embedding_model": dl_embeddings.model_name,
                    "user_id": user_id
                }
            )
            
            # Step 7: Save result (optional)
            if save_result and self.analysis_repository and user_id:
                result_id = await self.analysis_repository.save_result(result, user_id)
                result.processing_metadata["result_id"] = result_id
                logger.info(f"Result saved with ID: {result_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Body analysis failed: {str(e)}")
            raise BodyAnalysisError(f"Analysis failed: {str(e)}") from e


class GetAnalysisHistoryUseCase:
    """Use case for retrieving user's analysis history"""
    
    def __init__(self, analysis_repository: IAnalysisRepository):
        self.analysis_repository = analysis_repository
    
    async def execute(self, user_id: str, limit: int = 10) -> list[BodyAnalysisResult]:
        """Get user's analysis history"""
        try:
            history = await self.analysis_repository.get_user_history(user_id, limit)
            logger.info(f"Retrieved {len(history)} results for user {user_id}")
            return history
        except Exception as e:
            logger.error(f"Failed to get history for user {user_id}: {str(e)}")
            raise BodyAnalysisError(f"Failed to retrieve history: {str(e)}") from e


class ValidateImageUseCase:
    """Use case for image validation before analysis"""
    
    def __init__(self, image_processor: IImageProcessor):
        self.image_processor = image_processor
    
    def execute(self, image: np.ndarray) -> Dict[str, Any]:
        """Validate image and return validation result"""
        try:
            is_valid = self.image_processor.validate_image(image)
            
            validation_result = {
                "is_valid": is_valid,
                "image_shape": image.shape,
                "image_dtype": str(image.dtype),
                "recommendations": []
            }
            
            if not is_valid:
                validation_result["recommendations"].extend([
                    "Ensure image shows full torso (shoulders to hips)",
                    "Use good lighting and clear background",
                    "Person should face the camera directly"
                ])
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Image validation failed: {str(e)}")
            raise BodyAnalysisError(f"Validation failed: {str(e)}") from e
