"""
Infrastructure - Model Manager Implementation
Centralized ML model lifecycle management
"""

import logging
from typing import Dict, Optional
import asyncio
from pathlib import Path

from ...domain.interfaces import IModelManager
from .yolo_pose_extractor import YOLOPoseExtractor
from .resnet_extractor import ResNetFeatureExtractor
from .hybrid_classifier import SVMHybridClassifier
from .image_processor import ImageProcessor

logger = logging.getLogger(__name__)


def get_model_path(model_filename: str) -> str:
    """Get absolute path to model file"""
    # Try different possible locations for models
    possible_paths = [
        Path(__file__).parent.parent.parent.parent / "models" / model_filename,  # BodyAnalysisAI/models/
        Path(__file__).parent.parent.parent.parent.parent / "models" / model_filename,  # body-analysis-ai/models/
        Path(model_filename)  # Current directory
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path)
    
    # If not found, return the most logical path
    return str(possible_paths[1])  # body-analysis-ai/models/


class MLModelManager(IModelManager):
    """Centralized ML model management implementation"""
    
    def __init__(self, model_configs: Optional[Dict] = None):
        self.model_configs = model_configs or self._get_default_configs()
        
        # Model instances
        self.pose_extractor: Optional[YOLOPoseExtractor] = None
        self.feature_extractor: Optional[ResNetFeatureExtractor] = None
        self.classifier: Optional[SVMHybridClassifier] = None
        self.image_processor: Optional[ImageProcessor] = None
        
        # Model status tracking
        self._model_status = {
            'pose_extractor': False,
            'feature_extractor': False,
            'classifier': False,
            'image_processor': False
        }
    
    def _get_default_configs(self) -> Dict:
        """Get default model configurations"""
        return {
            'pose_extractor': {
                'model_path': get_model_path('yolov8m-pose.pt')
            },
            'feature_extractor': {
                'model_name': 'resnet50',
                'embedding_dim': 2048
            },
            'classifier': {
                'model_path': None  # Will use dummy model for development
            },
            'image_processor': {}
        }
    
    async def load_models(self) -> bool:
        """Load all required ML models"""
        try:
            logger.info("Starting ML model loading...")
            
            # Load models concurrently where possible
            loading_tasks = []
            
            # Load image processor (no heavy ML model)
            self._load_image_processor()
            
            # Load YOLO pose extractor
            loading_tasks.append(self._load_pose_extractor())
            
            # Load ResNet feature extractor  
            loading_tasks.append(self._load_feature_extractor())
            
            # Load classifier (lighter, can be loaded separately)
            self._load_classifier()
            
            # Wait for heavy model loading to complete
            await asyncio.gather(*loading_tasks, return_exceptions=True)
            
            # Update status
            self._update_model_status()
            
            loaded_count = sum(self._model_status.values())
            total_count = len(self._model_status)
            
            logger.info(f"Model loading completed: {loaded_count}/{total_count} models loaded")
            
            return loaded_count >= 3  # Require at least 3/4 models to be loaded
            
        except Exception as e:
            logger.error(f"Model loading failed: {str(e)}")
            return False
    
    async def _load_pose_extractor(self):
        """Load YOLO pose extraction model"""
        try:
            config = self.model_configs['pose_extractor']
            self.pose_extractor = YOLOPoseExtractor(
                model_path=config['model_path']
            )
            logger.info("YOLO pose extractor loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load pose extractor: {str(e)}")
            self.pose_extractor = None
    
    async def _load_feature_extractor(self):
        """Load ResNet feature extraction model"""
        try:
            config = self.model_configs['feature_extractor']
            self.feature_extractor = ResNetFeatureExtractor(
                model_name=config['model_name'],
                embedding_dim=config['embedding_dim']
            )
            logger.info("ResNet feature extractor loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load feature extractor: {str(e)}")
            self.feature_extractor = None
    
    def _load_classifier(self):
        """Load SVM classifier model"""
        try:
            config = self.model_configs['classifier']
            self.classifier = SVMHybridClassifier(
                model_path=config.get('model_path')
            )
            logger.info("SVM classifier loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load classifier: {str(e)}")
            self.classifier = None
    
    def _load_image_processor(self):
        """Load image processor (no ML model required)"""
        try:
            self.image_processor = ImageProcessor()
            logger.info("Image processor loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load image processor: {str(e)}")
            self.image_processor = None
    
    def _update_model_status(self):
        """Update model loading status"""
        self._model_status = {
            'pose_extractor': self.pose_extractor is not None and self.pose_extractor.is_model_loaded(),
            'feature_extractor': self.feature_extractor is not None and self.feature_extractor.is_model_loaded(),
            'classifier': self.classifier is not None and self.classifier.is_model_loaded(),
            'image_processor': self.image_processor is not None
        }
    
    def unload_models(self) -> None:
        """Unload all ML models to free memory"""
        try:
            logger.info("Unloading ML models...")
            
            # Clean up models
            if self.pose_extractor:
                del self.pose_extractor
                self.pose_extractor = None
            
            if self.feature_extractor:
                del self.feature_extractor
                self.feature_extractor = None
                
            if self.classifier:
                del self.classifier
                self.classifier = None
                
            if self.image_processor:
                del self.image_processor
                self.image_processor = None
            
            # Update status
            self._model_status = {key: False for key in self._model_status}
            
            logger.info("All models unloaded successfully")
            
        except Exception as e:
            logger.error(f"Error during model unloading: {str(e)}")
    
    def get_model_status(self) -> Dict[str, bool]:
        """Get loading status of all models"""
        self._update_model_status()  # Refresh status
        return self._model_status.copy()
    
    def validate_models(self) -> Dict[str, bool]:
        """Validate that all models are working correctly"""
        try:
            validation_results = {}
            
            # Validate pose extractor
            if self.pose_extractor:
                validation_results['pose_extractor'] = self.pose_extractor.is_model_loaded()
            else:
                validation_results['pose_extractor'] = False
            
            # Validate feature extractor
            if self.feature_extractor:
                validation_results['feature_extractor'] = self.feature_extractor.is_model_loaded()
            else:
                validation_results['feature_extractor'] = False
            
            # Validate classifier
            if self.classifier:
                validation_results['classifier'] = self.classifier.is_model_loaded()
            else:
                validation_results['classifier'] = False
            
            # Validate image processor
            validation_results['image_processor'] = self.image_processor is not None
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Model validation failed: {str(e)}")
            return {key: False for key in self._model_status}
    
    def get_model_instances(self) -> Dict:
        """Get all model instances for dependency injection"""
        return {
            'pose_extractor': self.pose_extractor,
            'feature_extractor': self.feature_extractor,
            'classifier': self.classifier,
            'image_processor': self.image_processor
        }
    
    def is_ready_for_analysis(self) -> bool:
        """Check if all essential models are ready for body analysis"""
        status = self.get_model_status()
        essential_models = ['pose_extractor', 'image_processor']
        
        return all(status.get(model, False) for model in essential_models)
    
    def get_model_info(self) -> Dict:
        """Get detailed information about all loaded models"""
        info = {}
        
        if self.pose_extractor:
            info['pose_extractor'] = {
                'version': self.pose_extractor.get_model_version(),
                'required_keypoints': self.pose_extractor.get_required_keypoints()
            }
        
        if self.feature_extractor:
            info['feature_extractor'] = self.feature_extractor.get_model_info()
        
        if self.classifier:
            info['classifier'] = self.classifier.get_model_info()
        
        if self.image_processor:
            info['image_processor'] = {
                'supported_formats': self.image_processor.get_supported_formats(),
                'max_image_size': self.image_processor.get_max_image_size()
            }
        
        return info
