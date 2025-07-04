import cv2
import numpy as np
import mediapipe as mp
from app.utils.helpers import get_xy, distance

mp_pose = mp.solutions.pose

def extract_metrics(image_bytes):
    npimg = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    h, w = image.shape[:2]

    with mp_pose.Pose(static_image_mode=True) as pose:
        results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if not results.pose_landmarks:
            return None

        lm = results.pose_landmarks.landmark

        shoulder = distance(get_xy(lm, mp_pose.PoseLandmark.LEFT_SHOULDER, w, h),
                            get_xy(lm, mp_pose.PoseLandmark.RIGHT_SHOULDER, w, h))
        waist = distance(get_xy(lm, mp_pose.PoseLandmark.LEFT_ELBOW, w, h),
                         get_xy(lm, mp_pose.PoseLandmark.RIGHT_ELBOW, w, h))
        hip = distance(get_xy(lm, mp_pose.PoseLandmark.LEFT_HIP, w, h),
                       get_xy(lm, mp_pose.PoseLandmark.RIGHT_HIP, w, h))

        return {
            "shoulder": round(shoulder, 2),
            "waist": round(waist, 2),
            "hip": round(hip, 2)
        }
