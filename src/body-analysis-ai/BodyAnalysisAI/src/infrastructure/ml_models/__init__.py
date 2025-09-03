"""
Infrastructure Layer - ML Models Implementation
Implements domain interfaces with actual ML models
"""

import cv2
import numpy as np
import torch
import torch.nn as nn
from ultralytics import YOLO
import torchvision.transforms as transforms
from torchvision import models
import joblib
import logging
from typing import Optional, Tuple
import asyncio
from concurrent.futures import ThreadPoolExecutor
import os

from ...domain.entities import (
    PoseKeypoints, 
    BodyRatios, 
    DLEmbeddings, 
    HybridFeatures, 
    BodyType,
    InsufficientKeypointsError,
    ModelLoadError
)
from ...domain.interfaces import (
    IPoseExtractor,
    IRatioCalculator,
    IDLFeatureExtractor,
    IHybridClassifier,
    IImageProcessor
)

logger = logging.getLogger(__name__)


class YOLOPoseExtractor(IPoseExtractor):
    """YOLO-based pose keypoint extraction"""
    
    def __init__(self, model_path: str = "yolov8m-pose.pt"):
        self.model_path = model_path
        self.model: Optional[YOLO] = None
        self.executor = ThreadPoolExecutor(max_workers=2)
        self._load_model()
    
    def _load_model(self):
        """Load YOLO pose model"""
        try:
            if os.path.exists(self.model_path):
                self.model = YOLO(self.model_path)
            else:
                raise ModelLoadError(f"Model file not found: {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {str(e)}")
            raise ModelLoadError(f"YOLO model loading failed: {str(e)}")
    
    async def extract_keypoints(self, image: np.ndarray) -> Optional[PoseKeypoints]:
        """Extract pose keypoints from image"""
        if self.model is None:
            raise ModelLoadError("YOLO model not loaded")
        
        try:
            # Run inference in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                self.executor, 
                self._run_inference, 
                image
            )
            
            if not results or len(results[0].keypoints) == 0:
                return None
            
            # Convert YOLO keypoints to our format
            keypoints_data = results[0].keypoints.data[0].cpu().numpy()
            confidence = float(results[0].boxes.conf[0]) if results[0].boxes else 0.8
            
            keypoints_dict = self._convert_yolo_keypoints(keypoints_data, image.shape)
            
            return PoseKeypoints(
                keypoints=keypoints_dict,
                image_dimensions=(image.shape[1], image.shape[0]),
                detection_confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Keypoint extraction failed: {str(e)}")
            return None
    
    def _run_inference(self, image: np.ndarray):
        """Run YOLO inference"""
        return self.model(image, verbose=False)
    
    def _convert_yolo_keypoints(self, keypoints_data: np.ndarray, image_shape: tuple) -> dict:
        """Convert YOLO keypoints format to our format"""
        # COCO pose keypoints mapping
        keypoint_names = [
            'nose', 'left_eye', 'right_eye', 'left_ear', 'right_ear',
            'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
            'left_wrist', 'right_wrist', 'left_hip', 'right_hip',
            'left_knee', 'right_knee', 'left_ankle', 'right_ankle'
        ]
        
        keypoints_dict = {}
        height, width = image_shape[:2]
        
        for i, name in enumerate(keypoint_names):
            if i < len(keypoints_data):
                x, y, conf = keypoints_data[i]
                # Normalize coordinates
                x_norm = float(x) / width
                y_norm = float(y) / height
                keypoints_dict[name] = (x_norm, y_norm, float(conf))
        
        return keypoints_dict
    
    def validate_keypoints(self, keypoints: PoseKeypoints) -> bool:
        """Validate if keypoints are sufficient for body analysis"""
        essential_keypoints = [
            'left_shoulder', 'right_shoulder', 
            'left_hip', 'right_hip'
        ]
        
        valid_count = sum(
            1 for kp_name in essential_keypoints 
            if keypoints.is_keypoint_valid(kp_name, min_confidence=0.5)
        )
        
        return valid_count >= 3  # At least 3 out of 4 essential keypoints


class BodyRatioCalculator(IRatioCalculator):
    """Calculate body ratios from pose keypoints"""
    
    def calculate_ratios(self, keypoints: PoseKeypoints) -> BodyRatios:
        """Calculate body ratios from pose keypoints"""
        try:
            # Get key body landmarks
            left_shoulder = keypoints.get_keypoint('left_shoulder')
            right_shoulder = keypoints.get_keypoint('right_shoulder')
            left_hip = keypoints.get_keypoint('left_hip')
            right_hip = keypoints.get_keypoint('right_hip')
            
            if not all([left_shoulder, right_shoulder, left_hip, right_hip]):
                raise InsufficientKeypointsError("Missing essential keypoints for ratio calculation")
            
            # Calculate measurements
            shoulder_width = self._calculate_distance(left_shoulder, right_shoulder)
            hip_width = self._calculate_distance(left_hip, right_hip)
            
            # Estimate waist width (typically 0.7-0.8 of hip width)
            waist_width = hip_width * 0.75
            
            # Calculate torso length
            shoulder_center_y = (left_shoulder[1] + right_shoulder[1]) / 2
            hip_center_y = (left_hip[1] + right_hip[1]) / 2
            torso_height = abs(hip_center_y - shoulder_center_y)
            
            # Calculate ratios
            shoulder_to_hip_ratio = shoulder_width / hip_width if hip_width > 0 else 1.0
            waist_to_hip_ratio = waist_width / hip_width if hip_width > 0 else 1.0
            shoulder_to_waist_ratio = shoulder_width / waist_width if waist_width > 0 else 1.0
            torso_aspect_ratio = torso_height / shoulder_width if shoulder_width > 0 else 1.0
            
            return BodyRatios(
                shoulder_to_hip_ratio=shoulder_to_hip_ratio,
                waist_to_hip_ratio=waist_to_hip_ratio,
                shoulder_to_waist_ratio=shoulder_to_waist_ratio,
                torso_aspect_ratio=torso_aspect_ratio
            )
            
        except Exception as e:
            logger.error(f"Ratio calculation failed: {str(e)}")
            raise InsufficientKeypointsError(f"Failed to calculate ratios: {str(e)}")
    
    def _calculate_distance(self, point1: tuple, point2: tuple) -> float:
        """Calculate Euclidean distance between two points"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


class ResNetFeatureExtractor(IDLFeatureExtractor):
    """ResNet-based deep learning feature extraction"""
    
    def __init__(self, model_name: str = "resnet50", embedding_dim: int = 512):
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
                self.model = models.resnet50(pretrained=True)
                # Remove final classification layer
                self.model = nn.Sequential(*list(self.model.children())[:-1])
            else:
                raise ModelLoadError(f"Unsupported model: {self.model_name}")
            
            self.model.eval()
            self.model.to(self.device)
            
            # Define image preprocessing
            self.transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                   std=[0.229, 0.224, 0.225])
            ])
            
        except Exception as e:
            logger.error(f"Failed to load ResNet model: {str(e)}")
            raise ModelLoadError(f"ResNet loading failed: {str(e)}")
    
    async def extract_embeddings(self, image: np.ndarray) -> DLEmbeddings:
        """Extract embeddings using ResNet backbone"""
        if self.model is None:
            raise ModelLoadError("ResNet model not loaded")
        
        try:
            # Run inference in thread pool
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                self.executor,
                self._extract_features,
                image
            )
            
            return DLEmbeddings(
                embeddings=embeddings,
                model_name=self.model_name,
                embedding_dimension=len(embeddings)
            )
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {str(e)}")
            raise ModelLoadError(f"Failed to extract features: {str(e)}")
    
    def _extract_features(self, image: np.ndarray) -> np.ndarray:
        """Extract features from image"""
        # Preprocess image
        if len(image.shape) == 3 and image.shape[2] == 3:
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image
        
        # Apply transforms
        input_tensor = self.transform(image_rgb).unsqueeze(0).to(self.device)
        
        # Extract features
        with torch.no_grad():
            features = self.model(input_tensor)
            features = features.squeeze().cpu().numpy()
        
        return features
    
    def get_embedding_dimension(self) -> int:
        """Get dimension of embeddings"""
        return self.embedding_dim


class SVMHybridClassifier(IHybridClassifier):
    """SVM-based hybrid feature classifier"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.is_trained = False
        self._load_model()
    
    def _load_model(self):
        """Load trained SVM model"""
        if self.model_path and os.path.exists(self.model_path):
            try:
                model_data = joblib.load(self.model_path)
                self.model = model_data['classifier']
                self.scaler = model_data['scaler']
                self.is_trained = True
            except Exception as e:
                logger.warning(f"Failed to load SVM model: {str(e)}")
                self._create_dummy_model()
        else:
            self._create_dummy_model()
    
    def _create_dummy_model(self):
        """Create dummy model for development"""
        from sklearn.svm import SVC
        from sklearn.preprocessing import StandardScaler
        
        self.model = SVC(probability=True, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    async def classify(self, features: HybridFeatures) -> Tuple[BodyType, float]:
        """Classify body type from hybrid features"""
        try:
            # Combine features
            feature_vector = features.to_combined_vector().reshape(1, -1)
            
            if not self.is_trained:
                # Return dummy classification for development
                return self._dummy_classify(features.body_ratios)
            
            # Scale features
            scaled_features = self.scaler.transform(feature_vector)
            
            # Predict
            prediction = self.model.predict(scaled_features)[0]
            probabilities = self.model.predict_proba(scaled_features)[0]
            confidence = float(max(probabilities))
            
            # Convert prediction to BodyType
            body_type = BodyType(prediction)
            
            return body_type, confidence
            
        except Exception as e:
            logger.error(f"Classification failed: {str(e)}")
            # Fallback to rule-based classification
            return self._dummy_classify(features.body_ratios)
    
    def _dummy_classify(self, ratios: BodyRatios) -> Tuple[BodyType, float]:
        """Dummy rule-based classification for development"""
        shoulder_hip = ratios.shoulder_to_hip_ratio
        waist_hip = ratios.waist_to_hip_ratio
        
        if shoulder_hip > 1.1 and waist_hip < 0.8:
            return BodyType.INVERTED_TRIANGLE, 0.75
        elif shoulder_hip < 0.9 and waist_hip < 0.8:
            return BodyType.PEAR, 0.75
        elif waist_hip > 0.85:
            return BodyType.APPLE, 0.75
        elif 0.9 <= shoulder_hip <= 1.1 and waist_hip < 0.75:
            return BodyType.HOURGLASS, 0.75
        else:
            return BodyType.RECTANGLE, 0.75
    
    def is_model_loaded(self) -> bool:
        """Check if classification model is loaded"""
        return self.model is not None


class ImageProcessor(IImageProcessor):
    """Image preprocessing and validation"""
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for analysis"""
        # Resize if too large
        height, width = image.shape[:2]
        max_size = 1024
        
        if max(height, width) > max_size:
            scale = max_size / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        # Ensure image is in BGR format (OpenCV default)
        if len(image.shape) == 3 and image.shape[2] == 4:
            # Convert RGBA to BGR
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
        elif len(image.shape) == 3 and image.shape[2] == 3:
            # Assume RGB, convert to BGR
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        return image
    
    def validate_image(self, image: np.ndarray) -> bool:
        """Validate image quality and format"""
        if image is None or image.size == 0:
            return False
        
        # Check dimensions
        if len(image.shape) not in [2, 3]:
            return False
        
        height, width = image.shape[:2]
        
        # Check minimum size
        if height < 200 or width < 200:
            return False
        
        # Check aspect ratio (should be roughly portrait or square)
        aspect_ratio = height / width
        if aspect_ratio < 0.5 or aspect_ratio > 3.0:
            return False
        
        return True
