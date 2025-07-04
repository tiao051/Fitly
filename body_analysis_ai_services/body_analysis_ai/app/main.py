from fastapi import FastAPI
from app.routes.analyze import router as analyze_router

app = FastAPI(
    title="Body Analysis AI Service",
    description="Extract body measurements from image and classify body shape/type.",
    version="1.0.0"
)

app.include_router(analyze_router)
