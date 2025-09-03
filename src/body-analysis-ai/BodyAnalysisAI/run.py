#!/usr/bin/env python3
"""
Body Analysis AI Service v2.0.0
Clean Architecture with Hybrid DL+ML Approach

Main entry point for the body type classification system using:
- YOLO Pose for keypoint extraction  
- ResNet backbone for deep learning embeddings
- SVM classifier for hybrid feature classification
- Clean Architecture principles
"""

import sys
import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path

# Add src directory to Python path for clean imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.presentation.api import router as body_analysis_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('body_analysis.log')
    ]
)

logger = logging.getLogger(__name__)

async def lifespan_startup():
    """Initialize application on startup"""
    logger.info("Starting Body Analysis AI Service v2.0.0")
    logger.info("Architecture: Clean Architecture with Hybrid DL+ML")
    logger.info("Features: YOLO Pose + ResNet + SVM Classification")
    
    # Create necessary directories
    directories = ["data", "models", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    logger.info("Service startup completed")

async def lifespan_shutdown():
    """Cleanup on shutdown"""
    logger.info("Shutting down Body Analysis AI Service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    await lifespan_startup()
    yield
    # Shutdown  
    await lifespan_shutdown()

# Create FastAPI application
app = FastAPI(
    title="Body Analysis AI Service",
    description="AI-powered body type classification using hybrid DL+ML approach",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(body_analysis_router, prefix="/body", tags=["Body Analysis"])

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "message": "Body Analysis AI Service v2.0.0",
        "description": "Hybrid DL+ML body type classification",
        "architecture": "Clean Architecture",
        "features": [
            "YOLO Pose keypoint extraction",
            "ResNet deep learning embeddings", 
            "SVM hybrid classification",
            "Body ratio analysis",
            "Analysis history tracking"
        ],
        "endpoints": {
            "analyze": "/body/analyze",
            "validate": "/body/validate", 
            "history": "/body/history/{user_id}",
            "trends": "/body/trends/{user_id}",
            "health": "/body/health",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "run:app",
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )