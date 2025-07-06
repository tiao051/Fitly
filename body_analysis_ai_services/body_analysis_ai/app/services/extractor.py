import cv2
import numpy as np
from ultralytics import YOLO
import cv2
import numpy as np
from ultralytics import YOLO

# Sử dụng model nhỏ hơn cho performance tốt hơn
model = YOLO('yolov8m-pose.pt')  # Nano model - nhanh hơn 3x

# Chỉ quan tâm keypoints cần thiết cho body shape
ESSENTIAL_KEYPOINTS = [5, 6, 7, 8, 11, 12]  # LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_ELBOW, RIGHT_ELBOW, LEFT_HIP, RIGHT_HIP

def resize_for_inference(image, target_size=640):
    """
    Resize ảnh để inference nhanh hơn
    """
    h, w = image.shape[:2]
    if max(h, w) > target_size:
        scale = target_size / max(h, w)
        new_h, new_w = int(h * scale), int(w * scale)
        resized = cv2.resize(image, (new_w, new_h))
        return resized, scale
    return image, 1.0

def extract_landmarks_optimized(image):
    """
    Optimized landmark extraction - focus on essential keypoints only
    """
    try:
        # Resize image for faster inference
        resized_image, scale = resize_for_inference(image)
        
        # Run inference on smaller image
        results = model(resized_image, verbose=False)
        
        if not results or len(results) == 0:
            return None
            
        result = results[0]
        
        if result.keypoints is None or len(result.keypoints.data) == 0:
            return None
            
        keypoints = result.keypoints.data[0]  # First person
        
        # Convert to normalized coordinates (0-1)
        h_orig, w_orig = image.shape[:2]
        normalized_keypoints = []
        
        for i, kp in enumerate(keypoints):
            x, y, conf = kp
            
            # Adjust coordinates back to original image size
            x_norm = float(x / resized_image.shape[1])
            y_norm = float(y / resized_image.shape[0])
            confidence = float(conf)
            
            # Only store essential keypoints with high detail
            if i in ESSENTIAL_KEYPOINTS:
                normalized_keypoints.append({
                    'x': x_norm,
                    'y': y_norm,
                    'confidence': confidence,
                    'index': i,
                    'name': list(COCO_KEYPOINTS.keys())[list(COCO_KEYPOINTS.values()).index(i)]
                })
            else:
                # Placeholder for non-essential keypoints
                normalized_keypoints.append({
                    'x': x_norm,
                    'y': y_norm,
                    'confidence': confidence
                })
        
        return normalized_keypoints
        
    except Exception as e:
        print(f"Error in optimized pose extraction: {e}")
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
