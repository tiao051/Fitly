import cv2
import numpy as np
from ultralytics import YOLO
import logging
from typing import Dict, List, Any, Optional
import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class BodyAnalyzer:
    def __init__(self):
        self.model = None
        self.model_path = "yolov8m-pose.pt"
        self.executor = ThreadPoolExecutor(max_workers=2)
        
    def _load_model(self):
        """Load YOLOv8 pose model"""
        try:
            if self.model is None:
                logger.info("Loading YOLOv8 pose model...")
                
                # Model will be downloaded automatically by ultralytics if not found
                self.model = YOLO(self.model_path)
                logger.info("Model loaded successfully")
            return self.model
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise
    
    def _preprocess_image(self, image_data: bytes) -> np.ndarray:
        """Convert image bytes to numpy array"""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            # Decode image
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Could not decode image")
                
            return image
        except Exception as e:
            logger.error(f"Image preprocessing failed: {str(e)}")
            raise
    
    def _extract_pose_data(self, results) -> Dict[str, Any]:
        """Extract pose keypoints from YOLO results"""
        try:
            poses = []
            
            for result in results:
                if result.keypoints is not None:
                    keypoints = result.keypoints.data.cpu().numpy()
                    boxes = result.boxes.data.cpu().numpy() if result.boxes else None
                    
                    for i, pose_keypoints in enumerate(keypoints):
                        pose_data = {
                            "person_id": i,
                            "confidence": float(boxes[i][4]) if boxes is not None and i < len(boxes) else 0.0,
                            "keypoints": []
                        }
                        
                        # YOLOv8-pose keypoint names (COCO format)
                        keypoint_names = [
                            "nose", "left_eye", "right_eye", "left_ear", "right_ear",
                            "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
                            "left_wrist", "right_wrist", "left_hip", "right_hip",
                            "left_knee", "right_knee", "left_ankle", "right_ankle"
                        ]
                        
                        for j, (x, y, conf) in enumerate(pose_keypoints):
                            if j < len(keypoint_names):
                                pose_data["keypoints"].append({
                                    "name": keypoint_names[j],
                                    "x": float(x),
                                    "y": float(y),
                                    "confidence": float(conf)
                                })
                        
                        poses.append(pose_data)
            
            return {
                "poses": poses,
                "total_persons": len(poses)
            }
        except Exception as e:
            logger.error(f"Pose data extraction failed: {str(e)}")
            raise
    
    def _analyze_body_metrics(self, pose_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze body metrics from pose data"""
        try:
            analysis_results = []
            
            for pose in pose_data["poses"]:
                keypoints = {kp["name"]: kp for kp in pose["keypoints"] if kp["confidence"] > 0.5}
                
                metrics = {
                    "person_id": pose["person_id"],
                    "pose_confidence": pose["confidence"],
                    "body_analysis": {}
                }
                
                # Basic body measurements analysis
                if "left_shoulder" in keypoints and "right_shoulder" in keypoints:
                    shoulder_width = abs(keypoints["left_shoulder"]["x"] - keypoints["right_shoulder"]["x"])
                    metrics["body_analysis"]["shoulder_width"] = float(shoulder_width)
                
                if "left_hip" in keypoints and "right_hip" in keypoints:
                    hip_width = abs(keypoints["left_hip"]["x"] - keypoints["right_hip"]["x"])
                    metrics["body_analysis"]["hip_width"] = float(hip_width)
                
                # Body posture analysis
                posture_analysis = self._analyze_posture(keypoints)
                metrics["body_analysis"]["posture"] = posture_analysis
                
                analysis_results.append(metrics)
            
            return {
                "analysis": analysis_results,
                "summary": {
                    "total_persons": len(analysis_results),
                    "avg_pose_confidence": np.mean([r["pose_confidence"] for r in analysis_results]) if analysis_results else 0
                }
            }
        except Exception as e:
            logger.error(f"Body metrics analysis failed: {str(e)}")
            raise
    
    def _analyze_posture(self, keypoints: Dict[str, Dict]) -> Dict[str, Any]:
        """Analyze body posture from keypoints"""
        try:
            posture = {
                "shoulder_alignment": "unknown",
                "hip_alignment": "unknown",
                "overall_posture": "unknown"
            }
            
            # Shoulder alignment
            if "left_shoulder" in keypoints and "right_shoulder" in keypoints:
                left_y = keypoints["left_shoulder"]["y"]
                right_y = keypoints["right_shoulder"]["y"]
                shoulder_diff = abs(left_y - right_y)
                
                if shoulder_diff < 10:  # threshold in pixels
                    posture["shoulder_alignment"] = "aligned"
                else:
                    posture["shoulder_alignment"] = "uneven"
            
            # Hip alignment
            if "left_hip" in keypoints and "right_hip" in keypoints:
                left_y = keypoints["left_hip"]["y"]
                right_y = keypoints["right_hip"]["y"]
                hip_diff = abs(left_y - right_y)
                
                if hip_diff < 10:  # threshold in pixels
                    posture["hip_alignment"] = "aligned"
                else:
                    posture["hip_alignment"] = "uneven"
            
            # Overall posture assessment
            if posture["shoulder_alignment"] == "aligned" and posture["hip_alignment"] == "aligned":
                posture["overall_posture"] = "good"
            elif posture["shoulder_alignment"] == "uneven" or posture["hip_alignment"] == "uneven":
                posture["overall_posture"] = "needs_attention"
            
            return posture
        except Exception as e:
            logger.error(f"Posture analysis failed: {str(e)}")
            return {"error": str(e)}
    
    def _run_inference(self, image: np.ndarray) -> Dict[str, Any]:
        """Run YOLO inference on image"""
        try:
            model = self._load_model()
            results = model(image, verbose=False)
            return self._extract_pose_data(results)
        except Exception as e:
            logger.error(f"Inference failed: {str(e)}")
            raise
    
    async def analyze_image(self, image_data: bytes) -> Dict[str, Any]:
        """Main analysis method"""
        try:
            # Preprocess image
            image = self._preprocess_image(image_data)
            
            # Run inference in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            pose_data = await loop.run_in_executor(
                self.executor, 
                self._run_inference, 
                image
            )
            
            # Analyze body metrics
            analysis = self._analyze_body_metrics(pose_data)
            
            return {
                "pose_data": pose_data,
                "body_analysis": analysis,
                "image_info": {
                    "height": image.shape[0],
                    "width": image.shape[1],
                    "channels": image.shape[2] if len(image.shape) > 2 else 1
                }
            }
        except Exception as e:
            logger.error(f"Image analysis failed: {str(e)}")
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Get analyzer status"""
        return {
            "model_loaded": self.model is not None,
            "model_path": self.model_path,
            "ready": True
        }
