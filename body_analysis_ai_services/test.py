import cv2
import mediapipe as mp

image = cv2.imread("data/test_data/v_taper1.jpg")

mp_pose = mp.solutions.pose
with mp_pose.Pose(static_image_mode=True) as pose:
    results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

if not results.pose_landmarks:
    print("❌ Không nhận diện được pose")
else:
    print("✅ Số lượng landmarks:", len(results.pose_landmarks.landmark))