from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from app.services.extractor import extract_metrics
from app.services.analyzer import analyze_body

router = APIRouter()

@router.post("/analyze")
async def analyze(image: UploadFile = File(...)):
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File is not an image.")

    metrics = extract_metrics(await image.read())
    if not metrics:
        raise HTTPException(status_code=422, detail="Could not extract body landmarks.")

    result = analyze_body(metrics)
    result["metrics"] = metrics
    return JSONResponse(content=result)
