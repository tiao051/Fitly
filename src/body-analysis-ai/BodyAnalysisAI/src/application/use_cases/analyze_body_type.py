"""
Application Use Case - Analyze Body Type
Main business logic for body type analysis
"""

from typing import Optional, Dict, Any
import numpy as np
import logging
import uuid
from datetime import datetime

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
    
    This use case orchestrates the complete workflow:
    1. Image preprocessing and validation
    2. Pose keypoint extraction
    3. Body ratio calculation
    4. Deep learning feature extraction
    5. Hybrid classification
    6. Result storage (optional)
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
        
        Args:
            image: Input image as numpy array
            user_id: Optional user identifier
            save_result: Whether to save result to repository
            
        Returns:
            BodyAnalysisResult containing all analysis data
            
        Raises:
            BodyAnalysisError: For general analysis errors
            InsufficientKeypointsError: When pose detection fails
        """
        try:
            analysis_id = str(uuid.uuid4())
            start_time = datetime.now()
            
            logger.info(f"Starting body analysis {analysis_id} for user {user_id}")
            
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
            
            logger.info(f"Extracted {len(pose_keypoints.keypoints)} keypoints")
            
            # Step 3: Calculate body ratios
            body_ratios = self.ratio_calculator.calculate_ratios(pose_keypoints)
            if not body_ratios.validate_ratios():
                raise BodyAnalysisError("Invalid body ratios calculated")
                
            logger.info("Body ratios calculated successfully")
            
            # Step 4: Extract DL embeddings
            dl_embeddings = await self.dl_feature_extractor.extract_features(processed_image)
            if not dl_embeddings.validate_embeddings():
                raise BodyAnalysisError("Invalid deep learning embeddings")
                
            logger.info(f"DL embeddings extracted: {dl_embeddings.embedding_dimension}D")
            
            # Step 5: Combine features and classify
            hybrid_features = HybridFeatures(
                dl_embeddings=dl_embeddings,
                body_ratios=body_ratios
            )
            
            if not hybrid_features.validate_features():
                raise BodyAnalysisError("Invalid hybrid features")
            
            # Perform classification
            body_type, confidence = await self.hybrid_classifier.classify(hybrid_features)
            
            # Step 6: Create result
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = BodyAnalysisResult(
                body_type=body_type,
                confidence_score=confidence,
                pose_keypoints=pose_keypoints,
                body_ratios=body_ratios,
                dl_embeddings=dl_embeddings,
                processing_metadata={
                    "analysis_id": analysis_id,
                    "user_id": user_id,
                    "processing_time_seconds": processing_time,
                    "timestamp": start_time.isoformat(),
                    "model_versions": {
                        "pose_model": self.pose_extractor.get_model_version(),
                        "dl_model": dl_embeddings.model_name,
                        "classifier_model": self.hybrid_classifier.get_model_version()
                    }
                }
            )
            
            # Step 7: Save result (optional)
            if save_result and self.analysis_repository:
                await self.analysis_repository.save_analysis(result)
                logger.info(f"Analysis result saved with ID: {analysis_id}")
            
            logger.info(f"Body analysis completed: {body_type.value} (confidence: {confidence:.3f})")
            
            return result
            
        except (BodyAnalysisError, InsufficientKeypointsError):
            # Re-raise domain exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error in body analysis: {str(e)}")
            raise BodyAnalysisError(f"Analysis failed: {str(e)}")
