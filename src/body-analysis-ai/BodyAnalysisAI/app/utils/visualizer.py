import cv2
import numpy as np
from typing import List, Dict, Tuple
from app.services.extractor import COCO_KEYPOINTS

# COCO keypoints connections (skeleton)
SKELETON_CONNECTIONS = [
    (0, 1), (0, 2), (1, 3), (2, 4),  # Head
    (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),  # Arms
    (5, 11), (6, 12), (11, 12),  # Torso
    (11, 13), (13, 15), (12, 14), (14, 16)  # Legs
]

KEYPOINT_COLORS = [
    (255, 0, 0),    # 0: nose - red
    (255, 85, 0),   # 1: left_eye - orange
    (255, 170, 0),  # 2: right_eye - yellow-orange
    (255, 255, 0),  # 3: left_ear - yellow
    (170, 255, 0),  # 4: right_ear - yellow-green
    (85, 255, 0),   # 5: left_shoulder - green
    (0, 255, 0),    # 6: right_shoulder - bright green
    (0, 255, 85),   # 7: left_elbow - green-cyan
    (0, 255, 170),  # 8: right_elbow - cyan-green
    (0, 255, 255),  # 9: left_wrist - cyan
    (0, 170, 255),  # 10: right_wrist - cyan-blue
    (0, 85, 255),   # 11: left_hip - blue
    (0, 0, 255),    # 12: right_hip - bright blue
    (85, 0, 255),   # 13: left_knee - blue-purple
    (170, 0, 255),  # 14: right_knee - purple-blue
    (255, 0, 255),  # 15: left_ankle - purple
    (255, 0, 170),  # 16: right_ankle - purple-red
]

KEYPOINT_NAMES = [
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle"
]

def draw_keypoints_on_image(image: np.ndarray, landmarks: List[Dict], confidence_threshold: float = 0.5) -> np.ndarray:
    """
    Vẽ keypoints và skeleton lên ảnh
    """
    img_copy = image.copy()
    h, w = img_copy.shape[:2]
    
    # Convert normalized coordinates to pixel coordinates
    keypoints_px = []
    for landmark in landmarks:
        if landmark['confidence'] >= confidence_threshold:
            x = int(landmark['x'] * w)
            y = int(landmark['y'] * h)
            keypoints_px.append((x, y, landmark['confidence']))
        else:
            keypoints_px.append(None)
    
    # Draw skeleton connections
    for connection in SKELETON_CONNECTIONS:
        start_idx, end_idx = connection
        if (keypoints_px[start_idx] is not None and 
            keypoints_px[end_idx] is not None):
            
            start_point = keypoints_px[start_idx][:2]
            end_point = keypoints_px[end_idx][:2]
            
            # Draw line with color based on confidence
            confidence = min(keypoints_px[start_idx][2], keypoints_px[end_idx][2])
            line_color = (0, int(255 * confidence), 0)
            
            cv2.line(img_copy, start_point, end_point, line_color, 2)
    
    # Draw keypoints
    for idx, keypoint in enumerate(keypoints_px):
        if keypoint is not None:
            x, y, confidence = keypoint
            color = KEYPOINT_COLORS[idx]
            
            # Draw circle with size based on confidence
            radius = max(3, int(8 * confidence))
            cv2.circle(img_copy, (x, y), radius, color, -1)
            
            # Draw confidence text
            cv2.putText(img_copy, f"{confidence:.2f}", 
                       (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.4, color, 1)
    
    return img_copy

def draw_body_measurements(image: np.ndarray, landmarks: List[Dict], measurements: Dict) -> np.ndarray:
    """
    Vẽ các đường đo trên ảnh
    """
    img_copy = image.copy()
    h, w = img_copy.shape[:2]
    
    # Helper function to get pixel coordinates
    def get_px_coords(keypoint_idx):
        landmark = landmarks[keypoint_idx]
        return (int(landmark['x'] * w), int(landmark['y'] * h))
    
    # Draw shoulder line
    try:
        left_shoulder = get_px_coords(COCO_KEYPOINTS['LEFT_SHOULDER'])
        right_shoulder = get_px_coords(COCO_KEYPOINTS['RIGHT_SHOULDER'])
        cv2.line(img_copy, left_shoulder, right_shoulder, (0, 255, 255), 3)
        
        # Add measurement text
        mid_shoulder = ((left_shoulder[0] + right_shoulder[0]) // 2, 
                       (left_shoulder[1] + right_shoulder[1]) // 2)
        cv2.putText(img_copy, f"Shoulder: {measurements['shoulder_width']:.1f}cm", 
                   (mid_shoulder[0] - 60, mid_shoulder[1] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    except Exception as e:
        print(f"Error drawing shoulder line: {e}")
    
    # Draw hip line
    try:
        left_hip = get_px_coords(COCO_KEYPOINTS['LEFT_HIP'])
        right_hip = get_px_coords(COCO_KEYPOINTS['RIGHT_HIP'])
        cv2.line(img_copy, left_hip, right_hip, (255, 0, 255), 3)
        
        # Add measurement text
        mid_hip = ((left_hip[0] + right_hip[0]) // 2, 
                  (left_hip[1] + right_hip[1]) // 2)
        cv2.putText(img_copy, f"Hip: {measurements['hip_width']:.1f}cm", 
                   (mid_hip[0] - 40, mid_hip[1] + 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
    except Exception as e:
        print(f"Error drawing hip line: {e}")
    
    # Draw waist line (estimated)
    try:
        left_hip = get_px_coords(COCO_KEYPOINTS['LEFT_HIP'])
        right_hip = get_px_coords(COCO_KEYPOINTS['RIGHT_HIP'])
        left_shoulder = get_px_coords(COCO_KEYPOINTS['LEFT_SHOULDER'])
        right_shoulder = get_px_coords(COCO_KEYPOINTS['RIGHT_SHOULDER'])
        
        # Waist is approximately 60% from shoulder to hip
        waist_y = int(left_shoulder[1] + 0.6 * (left_hip[1] - left_shoulder[1]))
        waist_left = (left_hip[0], waist_y)
        waist_right = (right_hip[0], waist_y)
        
        cv2.line(img_copy, waist_left, waist_right, (0, 255, 0), 3)
        
        # Add measurement text
        mid_waist = ((waist_left[0] + waist_right[0]) // 2, waist_y)
        cv2.putText(img_copy, f"Waist: {measurements['waist_width']:.1f}cm", 
                   (mid_waist[0] - 40, mid_waist[1] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    except Exception as e:
        print(f"Error drawing waist line: {e}")
    
    return img_copy

def get_keypoint_details(landmarks: List[Dict], image_shape: Tuple[int, int]) -> List[Dict]:
    """
    Trả về thông tin chi tiết về các keypoints
    """
    h, w = image_shape
    keypoint_info = []
    
    for i, landmark in enumerate(landmarks):
        keypoint_info.append({
            "index": i,
            "name": KEYPOINT_NAMES[i],
            "x_normalized": landmark['x'],
            "y_normalized": landmark['y'],
            "x_pixel": int(landmark['x'] * w),
            "y_pixel": int(landmark['y'] * h),
            "confidence": landmark['confidence']
        })
    
    return keypoint_info
