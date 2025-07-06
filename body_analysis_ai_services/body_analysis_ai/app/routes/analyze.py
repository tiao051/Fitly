from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
import numpy as np
import cv2
import io
from app.services.extractor import extract_landmarks_optimized
from app.services.analyzer import analyze_body_shape_optimized
from app.utils.helpers import validate_essential_keypoints

router = APIRouter()

@router.post("/analyze-fast")
async def analyze_fast(
    file: UploadFile = File(..., description="Ảnh chụp người (tối thiểu từ vai đến hông)"),
    return_image: bool = Form(False, description="Trả về ảnh có vẽ keypoints")
):
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        contents = await file.read()
        np_arr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Extract optimized landmarks
        landmarks = extract_landmarks_optimized(image)
        if landmarks is None:
            return {"error": "Không nhận diện được cơ thể trong ảnh."}

        # Validate essential keypoints
        validation = validate_essential_keypoints(landmarks)
        if not validation['is_valid']:
            return {
                "error": "Không đủ keypoints cần thiết",
                "missing_keypoints": validation['missing_keypoints'],
                "suggestion": "Vui lòng chụp ảnh bao gồm vai và hông rõ ràng"
            }
            
        # Fast analysis
        result = analyze_body_shape_optimized(landmarks, image.shape[:2])
        
        # Add validation info
        result["validation"] = validation
        
        # Return image if requested
        if return_image and "error" not in result:
            from app.utils.visualizer import draw_keypoints_on_image
            image_with_keypoints = draw_keypoints_on_image(image, landmarks)
            
            _, buffer = cv2.imencode('.jpg', image_with_keypoints)
            img_bytes = io.BytesIO(buffer.tobytes())
            
            return StreamingResponse(
                img_bytes, 
                media_type="image/jpeg",
                headers={
                    "X-Body-Shape": result.get("shape", "Unknown"),
                    "X-Analysis-Type": "optimized"
                }
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")