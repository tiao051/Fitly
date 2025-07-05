import math

def get_xy(landmarks, keypoint_index, image_shape):
    """
    Get x, y coordinates from YOLO pose landmarks
    """
    if keypoint_index >= len(landmarks):
        return None, None
        
    keypoint = landmarks[keypoint_index]
    
    # Convert normalized coordinates to pixel coordinates
    x = keypoint['x'] * image_shape[1]  # width
    y = keypoint['y'] * image_shape[0]  # height
    
    return x, y

def distance(p1, p2):
    """Calculate Euclidean distance between two points"""
    if p1[0] is None or p1[1] is None or p2[0] is None or p2[1] is None:
        return 0
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def get_keypoint_confidence(landmarks, keypoint_index):
    """Get confidence score for a specific keypoint"""
    if keypoint_index >= len(landmarks):
        return 0
    return landmarks[keypoint_index]['confidence']