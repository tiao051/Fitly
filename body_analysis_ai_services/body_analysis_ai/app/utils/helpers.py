import math

def get_xy_optimized(landmark, image_shape):
    """
    Optimized coordinate conversion - direct pixel calculation
    """
    h, w = image_shape
    x = int(landmark['x'] * w)
    y = int(landmark['y'] * h)
    return (x, y)

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

def classify_body_shape(r1, r2, additional_ratios=None):
    scores = {
        "V-shape (Inverted Triangle)": 0,
        "A-shape (Pear)": 0,
        "Hourglass": 0,
        "Rectangle": 0,
        "Apple": 0,
        "Oval": 0
    }
    
    # Scoring chính từ r1, r2
    ratio = r1 / r2 if r2 != 0 else 0
    
    # V-shape: vai rộng hơn hông
    if r1 > 1.3 and ratio > 1.15:
        scores["V-shape (Inverted Triangle)"] += 3
    
    # A-shape: hông rộng hơn vai
    if r2 > 1.3 and ratio < 0.85:
        scores["A-shape (Pear)"] += 3
    
    # Hourglass: vai và hông gần bằng nhau, cả hai đều lớn
    if abs(r1 - r2) < 0.2 and r1 > 1.2 and r2 > 1.2:
        scores["Hourglass"] += 3
    
    # Rectangle: vai và hông gần bằng nhau, không quá lớn
    if abs(r1 - r2) < 0.2 and 0.9 <= r1 <= 1.3 and 0.9 <= r2 <= 1.3:
        scores["Rectangle"] += 3
    
    # Apple: cả vai và hông đều nhỏ
    if r1 < 1.0 and r2 < 1.0:
        scores["Apple"] += 3
    
    # Scoring bổ sung từ keypoints khác
    if additional_ratios:
        # Tỷ lệ vai/hông trực tiếp
        if 'shoulder_hip_ratio' in additional_ratios:
            sh_ratio = additional_ratios['shoulder_hip_ratio']
            if sh_ratio > 1.25:  # Vai rộng hơn hông rõ rệt
                scores["V-shape (Inverted Triangle)"] += 2
            elif sh_ratio < 0.8:  # Hông rộng hơn vai rõ rệt
                scores["A-shape (Pear)"] += 2
            elif 0.9 <= sh_ratio <= 1.1:  # Vai và hông cân đối
                scores["Hourglass"] += 1
                scores["Rectangle"] += 1
        
        # Tỷ lệ elbow/waist (để phát hiện V-shape)
        if 'elbow_waist_ratio' in additional_ratios:
            ew_ratio = additional_ratios['elbow_waist_ratio']
            if ew_ratio > 1.2:  # Tay rộng -> V-shape
                scores["V-shape (Inverted Triangle)"] += 1
            elif ew_ratio < 0.9:  # Tay hẹp -> A-shape
                scores["A-shape (Pear)"] += 1
    
    # Trả về shape có điểm cao nhất
    best_shape = max(scores, key=scores.get)
    max_score = scores[best_shape]
    
    # Nếu điểm quá thấp -> Oval
    if max_score < 2:
        return "Oval"
    
    return best_shape

def validate_essential_keypoints(landmarks):
    """
    Validate essential keypoints for body shape analysis including elbow keypoints
    """
    from app.services.extractor import COCO_KEYPOINTS
    
    essential_indices = [
        COCO_KEYPOINTS['LEFT_SHOULDER'],
        COCO_KEYPOINTS['RIGHT_SHOULDER'],
        COCO_KEYPOINTS['LEFT_HIP'],
        COCO_KEYPOINTS['RIGHT_HIP'],
        COCO_KEYPOINTS['LEFT_ELBOW'],
        COCO_KEYPOINTS['RIGHT_ELBOW']
    ]
    
    min_confidence = 0.3
    validation_result = {
        'is_valid': True,
        'missing_keypoints': [],
        'low_confidence_keypoints': [],
        'confidence_scores': {}
    }
    
    for idx in essential_indices:
        confidence = get_keypoint_confidence(landmarks, idx)
        keypoint_name = [k for k, v in COCO_KEYPOINTS.items() if v == idx][0]
        
        validation_result['confidence_scores'][keypoint_name] = confidence
        
        if confidence < 0.1:  # Practically missing
            validation_result['missing_keypoints'].append(keypoint_name)
            validation_result['is_valid'] = False
        elif confidence < min_confidence:
            validation_result['low_confidence_keypoints'].append(keypoint_name)
    
    return validation_result