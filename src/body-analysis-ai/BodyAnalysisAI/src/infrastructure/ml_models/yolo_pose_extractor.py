"""
Infrastructure - YOLO Pose Extraction Implementation
YOLOv8-based pose keypoint extraction service
"""

import numpy as np
from ultralytics import YOLO
import logging
from typing import Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
import os

from ...domain.entities import PoseKeypoints, ModelLoadError
from ...domain.interfaces import IPoseExtractor

logger = logging.getLogger(__name__)


class YOLOPoseExtractor(IPoseExtractor):
    """YOLO-based pose keypoint extraction implementation"""
    
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
                logger.info(f"YOLO pose model loaded: {self.model_path}")
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
                logger.warning("No keypoints detected in image")
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
        """Run YOLO inference (blocking operation)"""
        return self.model(image, verbose=False)
    
    def _convert_yolo_keypoints(self, keypoints_data: np.ndarray, image_shape: tuple) -> dict:
        """Convert YOLO keypoints format to our domain format"""
        # COCO pose keypoints mapping (17 keypoints)
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
                # Normalize coordinates to [0, 1] range
                x_norm = float(x) / width if width > 0 else 0.0
                y_norm = float(y) / height if height > 0 else 0.0
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
        
        # Need at least 3 out of 4 essential keypoints for reliable analysis
        return valid_count >= 3
    
    def get_model_version(self) -> str:
        """Get the version/name of the pose extraction model"""
        return f"YOLOv8m-pose ({self.model_path})"
    
    def is_model_loaded(self) -> bool:
        """Check if the pose extraction model is loaded and ready"""
        return self.model is not None
    
    def get_required_keypoints(self) -> list[str]:
        """Get list of keypoints required for body analysis"""
        return [
            'left_shoulder', 'right_shoulder', 
            'left_hip', 'right_hip',
            'left_elbow', 'right_elbow',
            'left_knee', 'right_knee'
        ]
    
    def __del__(self):
        """Cleanup thread pool on object destruction"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
