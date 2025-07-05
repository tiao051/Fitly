from app.utils.helpers import get_xy, distance, get_keypoint_confidence
from app.services.extractor import COCO_KEYPOINTS

def analyze_body_shape(landmarks, image_shape, real_height_cm):
    # In debug landmarks
    if isinstance(landmarks[0], dict):
        for i, lm in enumerate(landmarks):
            print(f"Keypoint {i}: ({lm['x']:.3f}, {lm['y']:.3f}), confidence: {lm['confidence']:.3f}")
    else:
        for i, (x, y, conf) in enumerate(landmarks):
            print(f"Keypoint {i}: ({x:.3f}, {y:.3f}), confidence: {conf:.3f}")
    print("=== END DEBUG LANDMARKS ===")

    h, w = image_shape

    # Kiểm tra đầy đủ các điểm quan trọng
    required_indices = [
        COCO_KEYPOINTS['NOSE'],
        COCO_KEYPOINTS['LEFT_SHOULDER'],
        COCO_KEYPOINTS['RIGHT_SHOULDER'],
        COCO_KEYPOINTS['LEFT_HIP'],
        COCO_KEYPOINTS['RIGHT_HIP'],
        COCO_KEYPOINTS['LEFT_ANKLE'],
        COCO_KEYPOINTS['RIGHT_ANKLE']
    ]
    min_confidence = 0.3
    low_conf = [i for i in required_indices if get_keypoint_confidence(landmarks, i) < min_confidence]
    if low_conf:
        print(f"Low confidence keypoints: {low_conf}")
        return {"error": "Không thể phát hiện đầy đủ các điểm quan trọng trên cơ thể."}

    # Tính chiều cao ảnh bằng pixel
    if isinstance(landmarks[0], dict):
        nose_y = landmarks[COCO_KEYPOINTS['NOSE']]['y']
        left_ankle_y = landmarks[COCO_KEYPOINTS['LEFT_ANKLE']]['y']
        right_ankle_y = landmarks[COCO_KEYPOINTS['RIGHT_ANKLE']]['y']
    else:
        nose_y = landmarks[COCO_KEYPOINTS['NOSE']][1]
        left_ankle_y = landmarks[COCO_KEYPOINTS['LEFT_ANKLE']][1]
        right_ankle_y = landmarks[COCO_KEYPOINTS['RIGHT_ANKLE']][1]

    bottom_y = max(left_ankle_y, right_ankle_y)
    height_px = (bottom_y - nose_y) * h
    if height_px <= 0:
        return {"error": "Không thể tính toán chiều cao từ ảnh."}

    cm_per_px = real_height_cm / height_px

    # Tính số đo cơ thể
    shoulder_left = get_xy(landmarks, COCO_KEYPOINTS['LEFT_SHOULDER'], image_shape)
    shoulder_right = get_xy(landmarks, COCO_KEYPOINTS['RIGHT_SHOULDER'], image_shape)
    hip_left = get_xy(landmarks, COCO_KEYPOINTS['LEFT_HIP'], image_shape)
    hip_right = get_xy(landmarks, COCO_KEYPOINTS['RIGHT_HIP'], image_shape)

    shoulder_cm = distance(shoulder_left, shoulder_right) * cm_per_px
    hip_cm = distance(hip_left, hip_right) * cm_per_px
    waist_cm = hip_cm * 0.85  # Ước lượng eo

    # Kiểm tra tư thế
    if isinstance(landmarks[0], dict):
        shoulder_y_diff = abs(landmarks[COCO_KEYPOINTS['LEFT_SHOULDER']]['y'] - landmarks[COCO_KEYPOINTS['RIGHT_SHOULDER']]['y'])
        hip_y_diff = abs(landmarks[COCO_KEYPOINTS['LEFT_HIP']]['y'] - landmarks[COCO_KEYPOINTS['RIGHT_HIP']]['y'])
    else:
        shoulder_y_diff = abs(landmarks[COCO_KEYPOINTS['LEFT_SHOULDER']][1] - landmarks[COCO_KEYPOINTS['RIGHT_SHOULDER']][1])
        hip_y_diff = abs(landmarks[COCO_KEYPOINTS['LEFT_HIP']][1] - landmarks[COCO_KEYPOINTS['RIGHT_HIP']][1])
    
    if shoulder_y_diff > 0.05 or hip_y_diff > 0.05:
        return {"error": "Vui lòng đứng thẳng và quay trực diện với camera."}

    if shoulder_cm <= 0 or waist_cm <= 0:
        return {"error": "Không thể tính toán chính xác các số đo cơ thể."}

    # Phân loại hình thể
    r1 = shoulder_cm / waist_cm  # Tỉ lệ vai / eo
    r2 = hip_cm / waist_cm       # Tỉ lệ hông / eo

    if r1 > 1.3 and r2 < 1.1:
        shape = "V-shape (Inverted Triangle)"
    elif r1 < 1.1 and r2 > 1.3:
        shape = "A-shape (Pear)"
    elif r1 > 1.05 and abs(r1 - r2) < 0.2:
        shape = "Hourglass"
    elif abs(r1 - r2) < 0.15:
        shape = "Rectangle"
    elif waist_cm >= shoulder_cm and waist_cm >= hip_cm:
        shape = "Apple"
    else:
        shape = "Oval"

    return {
        "shoulder_cm": round(shoulder_cm, 2),
        "waist_cm": round(waist_cm, 2),
        "hip_cm": round(hip_cm, 2),
        "cm_per_px": round(cm_per_px, 4),
        "shape": shape,
        "measurements": {
            "shoulder_width": round(shoulder_cm, 2),
            "waist_width": round(waist_cm, 2),
            "hip_width": round(hip_cm, 2),
            "height": real_height_cm
        },
        "ratios": {
            "shoulder_waist": round(r1, 2),
            "hip_waist": round(r2, 2)
        }
    }
