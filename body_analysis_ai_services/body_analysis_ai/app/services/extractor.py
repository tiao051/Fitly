import cv2
import numpy as np
from ultralytics import YOLO

# Load YOLOv8 pose model
model = YOLO('yolov8n-pose.pt')  # nano version for faster inference

def extract_landmarks(image):
    """
    Extract pose landmarks using YOLOv8 Pose
    Returns keypoints in COCO format (17 keypoints)
    """
    try:
        # Run inference
        results = model(image, verbose=False)
        
        if not results or len(results) == 0:
            return None
            
        # Get the first detection (assuming single person)
        result = results[0]
        
        if result.keypoints is None or len(result.keypoints.data) == 0:
            return None
            
        # Get keypoints (shape: [num_persons, num_keypoints, 3])
        # [x, y, confidence] for each keypoint
        keypoints = result.keypoints.data[0]  # First person
        
        # Convert to normalized coordinates (0-1)
        h, w = image.shape[:2]
        normalized_keypoints = []
        
        for kp in keypoints:
            x, y, conf = kp
            # Normalize coordinates
            x_norm = float(x / w)
            y_norm = float(y / h)
            confidence = float(conf)
            
            normalized_keypoints.append({
                'x': x_norm,
                'y': y_norm,
                'confidence': confidence
            })
        
        return normalized_keypoints
        
    except Exception as e:
        print(f"Error in pose extraction: {e}")
        return None

# COCO Pose keypoint indices
COCO_KEYPOINTS = {
    'NOSE': 0,
    'LEFT_EYE': 1,
    'RIGHT_EYE': 2,
    'LEFT_EAR': 3,
    'RIGHT_EAR': 4,
    'LEFT_SHOULDER': 5,
    'RIGHT_SHOULDER': 6,
    'LEFT_ELBOW': 7,
    'RIGHT_ELBOW': 8,
    'LEFT_WRIST': 9,
    'RIGHT_WRIST': 10,
    'LEFT_HIP': 11,
    'RIGHT_HIP': 12,
    'LEFT_KNEE': 13,
    'RIGHT_KNEE': 14,
    'LEFT_ANKLE': 15,
    'RIGHT_ANKLE': 16
}
