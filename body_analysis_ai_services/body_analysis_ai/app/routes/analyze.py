from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
import numpy as np
import cv2
import io
from app.services.extractor import extract_landmarks
from app.services.analyzer import analyze_body_shape

router = APIRouter()

@router.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...), 
    height_cm: float = Form(...),
    return_image: bool = Form(False)
):
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Validate height
        if height_cm <= 0 or height_cm > 300:
            raise HTTPException(status_code=400, detail="Height must be between 1-300 cm")
        
        contents = await file.read()
        np_arr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Extract keypoints
        landmarks = extract_landmarks(image)
        if landmarks is None:
            return {"error": "Không nhận diện được cơ thể trong ảnh."}

        # Analyze
        result = analyze_body_shape(landmarks, image.shape[:2], height_cm)

        # Add keypoints info
        from app.utils.visualizer import get_keypoint_details
        keypoint_info = get_keypoint_details(landmarks, image.shape[:2])
        result["keypoints"] = keypoint_info
        result["image_info"] = {
            "width": image.shape[1],
            "height": image.shape[0],
            "total_keypoints": len(landmarks),
            "high_confidence_keypoints": len([kp for kp in keypoint_info if kp['confidence'] > 0.5])
        }

        # Nếu yêu cầu trả ảnh
        if return_image and "error" not in result:
            from app.utils.visualizer import draw_keypoints_on_image, draw_body_measurements

            image_with_keypoints = draw_keypoints_on_image(image, landmarks)

            if "measurements" in result:
                image_with_keypoints = draw_body_measurements(
                    image_with_keypoints, landmarks, result["measurements"]
                )

            _, buffer = cv2.imencode('.jpg', image_with_keypoints)
            img_bytes = io.BytesIO(buffer.tobytes())

            return StreamingResponse(
                img_bytes, 
                media_type="image/jpeg",
                headers={
                    "X-Analysis-Result": str(result).replace("'", '"'),
                    "X-Shape": result.get("shape", "Unknown"),
                    "X-Shoulder-Width": str(result.get("measurements", {}).get("shoulder_width", 0)),
                    "X-Hip-Width": str(result.get("measurements", {}).get("hip_width", 0))
                }
            )
        
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
