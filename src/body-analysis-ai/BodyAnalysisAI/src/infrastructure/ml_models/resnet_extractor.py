"""
Infrastructure - ResNet Feature Extractor Implementation
Deep learning feature extraction using ResNet backbone
"""

import cv2
import numpy as np
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models
import logging
from typing import Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

from ...domain.entities import ModelLoadError
from ...domain.interfaces import IDLFeatureExtractor

logger = logging.getLogger(__name__)


class ResNetFeatureExtractor(IDLFeatureExtractor):
    """ResNet-based deep learning feature extraction implementation"""
    
    def __init__(self, model_name: str = "resnet50", embedding_dim: int = 2048):
        self.model_name = model_name
        self.embedding_dim = embedding_dim
        self.model: Optional[nn.Module] = None
        self.transform = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.executor = ThreadPoolExecutor(max_workers=2)
        self._load_model()
    
    def _load_model(self):
        """Load pretrained ResNet model"""
        try:
            if self.model_name == "resnet50":
                # Load pretrained ResNet50
                self.model = models.resnet50(pretrained=True)
                # Remove final classification layer to get feature embeddings
                self.model = nn.Sequential(*list(self.model.children())[:-1])
                self.embedding_dim = 2048
            elif self.model_name == "resnet34":
                self.model = models.resnet34(pretrained=True)
                self.model = nn.Sequential(*list(self.model.children())[:-1])
                self.embedding_dim = 512
            elif self.model_name == "resnet18":
                self.model = models.resnet18(pretrained=True)
                self.model = nn.Sequential(*list(self.model.children())[:-1])
                self.embedding_dim = 512
            else:
                raise ModelLoadError(f"Unsupported ResNet model: {self.model_name}")
            
            # Set to evaluation mode and move to device
            self.model.eval()
            self.model.to(self.device)
            
            # Define image preprocessing pipeline
            self.transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize((224, 224)),  # ResNet input size
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],  # ImageNet means
                    std=[0.229, 0.224, 0.225]   # ImageNet stds
                )
            ])
            
            logger.info(f"ResNet model loaded: {self.model_name} on {self.device}")
            
        except Exception as e:
            logger.error(f"Failed to load ResNet model: {str(e)}")
            raise ModelLoadError(f"ResNet loading failed: {str(e)}")
    
    async def extract_features(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Extract deep learning features from image"""
        if self.model is None:
            raise ModelLoadError("ResNet model not loaded")
        
        try:
            # Run feature extraction in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            features = await loop.run_in_executor(
                self.executor,
                self._extract_features_sync,
                image
            )
            
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {str(e)}")
            return None
    
    def _extract_features_sync(self, image: np.ndarray) -> np.ndarray:
        """Synchronous feature extraction (blocking operation)"""
        try:
            # Preprocess image
            processed_image = self._preprocess_image(image)
            
            # Apply transforms and add batch dimension
            input_tensor = self.transform(processed_image).unsqueeze(0).to(self.device)
            
            # Extract features without gradient computation
            with torch.no_grad():
                features = self.model(input_tensor)
                # Flatten features and move to CPU
                features = features.squeeze().cpu().numpy()
            
            return features
            
        except Exception as e:
            logger.error(f"Sync feature extraction failed: {str(e)}")
            raise
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for ResNet input"""
        # Ensure image is in RGB format
        if len(image.shape) == 3:
            if image.shape[2] == 3:
                # Convert BGR to RGB if needed
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image
        else:
            # Convert grayscale to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        
        # Ensure uint8 format for PIL
        if image_rgb.dtype != np.uint8:
            image_rgb = (image_rgb * 255).astype(np.uint8)
        
        return image_rgb
    
    def get_feature_dimension(self) -> int:
        """Get the dimension of extracted features"""
        return self.embedding_dim
    
    def is_model_loaded(self) -> bool:
        """Check if the feature extraction model is loaded"""
        return self.model is not None
    
    def get_model_info(self) -> dict:
        """Get information about the feature extraction model"""
        return {
            'model_name': self.model_name,
            'embedding_dimension': self.embedding_dim,
            'device': str(self.device),
            'input_size': (224, 224),
            'preprocessing': 'ImageNet normalization',
            'is_loaded': self.is_model_loaded()
        }
    
    def get_supported_models(self) -> list[str]:
        """Get list of supported ResNet model variants"""
        return ['resnet18', 'resnet34', 'resnet50']
    
    def __del__(self):
        """Cleanup thread pool on object destruction"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
