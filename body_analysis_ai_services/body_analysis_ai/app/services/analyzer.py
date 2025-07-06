from app.utils.helpers import get_xy_optimized, distance, get_keypoint_confidence, classify_body_shape
from app.services.extractor import COCO_KEYPOINTS
from app.utils.pose_helpers import validate_pose

def analyze_body_shape_optimized(landmarks, image_shape):
    pose_issues = validate_pose(landmarks)
    if pose_issues:
        return {
            "valid": False,
            "pose_issues": pose_issues,
            "message": "Pose không hợp lệ, vui lòng chụp lại theo hướng dẫn."
        }
    
    # Keypoints bắt buộc (thêm elbow)
    required_indices = [
        COCO_KEYPOINTS['LEFT_SHOULDER'],
        COCO_KEYPOINTS['RIGHT_SHOULDER'], 
        COCO_KEYPOINTS['LEFT_HIP'],
        COCO_KEYPOINTS['RIGHT_HIP'],
        COCO_KEYPOINTS['LEFT_ELBOW'],    # Thêm
        COCO_KEYPOINTS['RIGHT_ELBOW']    # Thêm
    ]
    
    min_confidence = 0.3
    low_conf = [i for i in required_indices if get_keypoint_confidence(landmarks, i) < min_confidence]
    if low_conf:
        return {"error": "Không thể phát hiện vai, hông và tay. Vui lòng chụp ảnh bao gồm vùng torso đầy đủ."}

    # Lấy tọa độ pixel
    shoulder_left = get_xy_optimized(landmarks[COCO_KEYPOINTS['LEFT_SHOULDER']], image_shape)
    shoulder_right = get_xy_optimized(landmarks[COCO_KEYPOINTS['RIGHT_SHOULDER']], image_shape)
    hip_left = get_xy_optimized(landmarks[COCO_KEYPOINTS['LEFT_HIP']], image_shape)
    hip_right = get_xy_optimized(landmarks[COCO_KEYPOINTS['RIGHT_HIP']], image_shape)
    elbow_left = get_xy_optimized(landmarks[COCO_KEYPOINTS['LEFT_ELBOW']], image_shape)
    elbow_right = get_xy_optimized(landmarks[COCO_KEYPOINTS['RIGHT_ELBOW']], image_shape)

    # Tính khoảng cách trong pixels
    shoulder_px = distance(shoulder_left, shoulder_right)
    hip_px = distance(hip_left, hip_right)
    elbow_px = distance(elbow_left, elbow_right)
    waist_px = hip_px * 0.85  # Ước tính eo

    # Kiểm tra tư thế
    shoulder_y_diff = abs(landmarks[COCO_KEYPOINTS['LEFT_SHOULDER']]['y'] - 
                         landmarks[COCO_KEYPOINTS['RIGHT_SHOULDER']]['y'])
    hip_y_diff = abs(landmarks[COCO_KEYPOINTS['LEFT_HIP']]['y'] - 
                    landmarks[COCO_KEYPOINTS['RIGHT_HIP']]['y'])

    if shoulder_y_diff > 0.05 or hip_y_diff > 0.05:
        return {"error": "Vui lòng đứng thẳng và quay trực diện với camera."}

    if shoulder_px <= 0 or waist_px <= 0 or elbow_px <= 0:
        return {"error": "Không thể tính toán chính xác các số đo cơ thể."}

    # Tính ratios
    r1 = shoulder_px / waist_px  # Shoulder to waist ratio
    r2 = hip_px / waist_px       # Hip to waist ratio
    
    # Thêm tỷ lệ bổ sung
    additional_ratios = {
        'shoulder_hip_ratio': shoulder_px / hip_px if hip_px > 0 else 0,
        'elbow_waist_ratio': elbow_px / waist_px if waist_px > 0 else 0
    }
    
    # Phân loại body shape với thêm tỷ lệ
    shape = classify_body_shape(r1, r2, additional_ratios)

    return {
        "shape": shape,
        "analysis_type": "optimized",
        "ratios": {
            "shoulder_waist": round(r1, 2),
            "hip_waist": round(r2, 2),
            "shoulder_hip": round(additional_ratios['shoulder_hip_ratio'], 2),
            "elbow_waist": round(additional_ratios['elbow_waist_ratio'], 2)
        },
        "confidence_scores": {
            "left_shoulder": landmarks[COCO_KEYPOINTS['LEFT_SHOULDER']]['confidence'],
            "right_shoulder": landmarks[COCO_KEYPOINTS['RIGHT_SHOULDER']]['confidence'],
            "left_hip": landmarks[COCO_KEYPOINTS['LEFT_HIP']]['confidence'],
            "right_hip": landmarks[COCO_KEYPOINTS['RIGHT_HIP']]['confidence'],
            "left_elbow": landmarks[COCO_KEYPOINTS['LEFT_ELBOW']]['confidence'],
            "right_elbow": landmarks[COCO_KEYPOINTS['RIGHT_ELBOW']]['confidence']
        }
    }