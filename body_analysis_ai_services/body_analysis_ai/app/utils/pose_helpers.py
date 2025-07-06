import math
from app.services.extractor import COCO_KEYPOINTS

def get_angle(p1, p2):
    dx = p2['x'] - p1['x']
    dy = p2['y'] - p1['y']
    angle_rad = math.atan2(dy, dx)
    angle_deg = abs(math.degrees(angle_rad))

    # Normalize angle to [0, 90] — nghiêng trái hay phải đều tính như nhau
    if angle_deg > 90:
        angle_deg = 180 - angle_deg

    return angle_deg

def get_keypoint_by_name(keypoints, name):
    """
    Lấy keypoint theo tên từ list landmarks
    """
    index = COCO_KEYPOINTS[name]
    if index < len(keypoints):
        return keypoints[index]
    return None

def is_pose_tilted(keypoints, threshold=20):
    issues = []
    angles = {}

    left_shoulder = get_keypoint_by_name(keypoints, 'LEFT_SHOULDER')
    right_shoulder = get_keypoint_by_name(keypoints, 'RIGHT_SHOULDER')
    left_hip = get_keypoint_by_name(keypoints, 'LEFT_HIP')
    right_hip = get_keypoint_by_name(keypoints, 'RIGHT_HIP')

    # Shoulder angle
    if left_shoulder and right_shoulder and left_shoulder['confidence'] > 0.3 and right_shoulder['confidence'] > 0.3:
        shoulder_angle = get_angle(left_shoulder, right_shoulder)
        angles['shoulder_angle'] = shoulder_angle
        if shoulder_angle > threshold:
            issues.append(f"Tilted shoulders ({shoulder_angle:.2f}°)")

    # Hip angle
    if left_hip and right_hip and left_hip['confidence'] > 0.3 and right_hip['confidence'] > 0.3:
        hip_angle = get_angle(left_hip, right_hip)
        angles['hip_angle'] = hip_angle
        if hip_angle > threshold:
            issues.append(f"Tilted hips ({hip_angle:.2f}°)")

    return issues, angles


def is_twisted_body(keypoints, shoulder_hip_ratio_threshold=1.3):
    left_shoulder = get_keypoint_by_name(keypoints, 'LEFT_SHOULDER')
    right_shoulder = get_keypoint_by_name(keypoints, 'RIGHT_SHOULDER')
    left_hip = get_keypoint_by_name(keypoints, 'LEFT_HIP')
    right_hip = get_keypoint_by_name(keypoints, 'RIGHT_HIP')

    if not all([left_shoulder, right_shoulder, left_hip, right_hip]):
        return False, None

    if any(kp['confidence'] < 0.3 for kp in [left_shoulder, right_shoulder, left_hip, right_hip]):
        return False, None

    shoulder_width = abs(left_shoulder['x'] - right_shoulder['x'])
    hip_width = abs(left_hip['x'] - right_hip['x'])

    if hip_width == 0:
        return False, None

    ratio = shoulder_width / hip_width
    return ratio > shoulder_hip_ratio_threshold, ratio

def validate_pose(keypoints):
    issues = []
    diagnostics = {}

    # Tilt
    tilt_issues, tilt_angles = is_pose_tilted(keypoints)
    issues.extend(tilt_issues)
    diagnostics.update(tilt_angles)

    # Twist
    twisted, twist_ratio = is_twisted_body(keypoints)
    if twist_ratio:
        diagnostics['shoulder_hip_ratio'] = twist_ratio
    if twisted:
        issues.append(f"Body is rotated (shoulder/hip ratio = {twist_ratio:.2f})")
        
    return {
        "pose_issues": issues,
        "diagnostics": diagnostics,
        "valid": len(issues) == 0
    }
