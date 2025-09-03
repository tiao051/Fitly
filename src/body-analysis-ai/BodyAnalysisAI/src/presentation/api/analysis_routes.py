"""
Presentation Layer - Analysis API Routes
FastAPI routes for body analysis operations
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
import numpy as np
import cv2
from PIL import Image
import io
import logging
from typing import Optional

from ..dto import (
    AnalysisResponseDto,
    BodyRatiosDto,
    ErrorResponseDto
)
from .dependencies import dependency_provider, DependencyProvider
from ...domain.entities import BodyAnalysisError, InsufficientKeypointsError, ModelLoadError

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/analysis", tags=["analysis"])


def get_dependency_provider() -> DependencyProvider:
    """FastAPI dependency to get provider"""
    return dependency_provider


async def convert_upload_to_numpy(file: UploadFile) -> np.ndarray:
    """Convert uploaded file to numpy array"""
    try:
        # Read file contents
        contents = await file.read()
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(contents))
        
        # Convert to numpy array
        image_array = np.array(image)
        
        # Ensure proper format
        if len(image_array.shape) == 3:
            if image_array.shape[2] == 4:  # RGBA
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGBA2RGB)
            elif image_array.shape[2] == 3:  # RGB
                pass  # Keep as is
        
        return image_array
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")


@router.post("/", response_model=AnalysisResponseDto)
async def analyze_body_type(
    file: UploadFile = File(..., description="Body image for analysis"),
    user_id: Optional[str] = Form(None, description="Optional user identifier"),
    save_result: bool = Form(True, description="Whether to save the result"),
    provider: DependencyProvider = Depends(get_dependency_provider)
):
    """
    Analyze body type from uploaded image using hybrid DL+ML approach
    
    - **file**: Image file (JPEG, PNG) showing full torso
    - **user_id**: Optional user identifier for tracking
    - **save_result**: Whether to save the analysis result
    
    Returns:
        AnalysisResponseDto containing body type, confidence, and measurements
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Check if dependencies are ready
        if not provider.is_ready():
            await provider.initialize_dependencies()
        
        # Convert to numpy array
        image = await convert_upload_to_numpy(file)
        
        # Get use case and execute analysis
        use_case = provider.get_analyze_use_case()
        result = await use_case.execute(image, user_id, save_result)
        
        # Convert to DTO
        response = AnalysisResponseDto(
            body_type=result.body_type.value,
            confidence_score=result.confidence_score,
            body_ratios=BodyRatiosDto(
                shoulder_to_hip_ratio=result.body_ratios.shoulder_to_hip_ratio,
                waist_to_hip_ratio=result.body_ratios.waist_to_hip_ratio,
                shoulder_to_waist_ratio=result.body_ratios.shoulder_to_waist_ratio,
                torso_aspect_ratio=result.body_ratios.torso_aspect_ratio
            ),
            keypoints_detected=len(result.pose_keypoints.keypoints),
            detection_confidence=result.pose_keypoints.detection_confidence,
            processing_metadata=result.processing_metadata,
            result_id=result.processing_metadata.get("analysis_id")
        )
        
        logger.info(f"Analysis completed for user {user_id}: {result.body_type.value}")
        return response
        
    except (BodyAnalysisError, InsufficientKeypointsError, ModelLoadError) as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/validate", response_model=dict)
async def validate_image(
    file: UploadFile = File(..., description="Image to validate"),
    provider: DependencyProvider = Depends(get_dependency_provider)
):
    """
    Validate image quality and format before analysis
    
    - **file**: Image file to validate
    
    Returns:
        Validation results and recommendations
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Check if dependencies are ready
        if not provider.is_ready():
            await provider.initialize_dependencies()
        
        # Convert to numpy array
        image = await convert_upload_to_numpy(file)
        
        # Get use case and execute validation
        use_case = provider.get_validation_use_case()
        validation_result = use_case.execute(image)
        
        logger.info(f"Image validation completed: valid={validation_result['is_valid']}")
        return validation_result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")
