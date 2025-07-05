from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import numpy as np
import cv2

from app.services.extractor import extract_landmarks
from app.services.analyzer import analyze_body_shape

router = APIRouter()

@router.post("/analyze")
async def analyze_image(file: UploadFile = File(...), height_cm: float = Form(...)):
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
        
        landmarks = extract_landmarks(image)
        if landmarks is None:
            return {"error": "Không nhận diện được cơ thể trong ảnh."}

        result = analyze_body_shape(landmarks, image.shape[:2], height_cm)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")