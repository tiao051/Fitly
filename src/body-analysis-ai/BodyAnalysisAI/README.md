# Body Analysis AI Service

**Clean Architecture** • **Hybrid DL+ML** • **Body Type Classification**

A sophisticated body type classification system built with Clean Architecture principles, combining deep learning embeddings with traditional machine learning for accurate body shape analysis.

## 🚀 Features

### Hybrid Classification Approach
- **YOLO Pose**: Advanced pose keypoint extraction
- **ResNet Backbone**: Deep learning feature embeddings  
- **SVM Classifier**: Hybrid feature classification
- **Body Ratios**: Traditional anthropometric measurements

### Clean Architecture Benefits
- **Separation of Concerns**: Clear layer boundaries
- **Testability**: Easy unit testing for each component
- **Maintainability**: Modular, extensible design
- **Flexibility**: Easy to swap ML models or add features

### Body Type Categories
- **Hourglass**: Balanced shoulders & hips, defined waist
- **Apple**: Fuller midsection, broader torso
- **Pear**: Hips wider than shoulders
- **Rectangle**: Similar shoulder, waist & hip measurements
- **Inverted Triangle**: Shoulders broader than hips

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────┐
│         Presentation Layer          │
│    (FastAPI, DTOs, API Routes)      │
└─────────────────────────────────────┘
                    │
┌─────────────────────────────────────┐
│        Application Layer            │
│   (Use Cases, Business Services)    │
└─────────────────────────────────────┘
                    │
┌─────────────────────────────────────┐
│          Domain Layer               │
│   (Entities, Interfaces, Rules)     │
└─────────────────────────────────────┘
                    │
┌─────────────────────────────────────┐
│       Infrastructure Layer          │
│  (ML Models, Repositories, Data)    │
└─────────────────────────────────────┘
```

## 📁 Project Structure

```
src/
├── domain/                 # Core Business Logic
│   ├── entities/          # Business entities (BodyType, PoseKeypoints, etc.)
│   └── interfaces/        # Abstract interfaces for external dependencies
├── application/            # Application Logic
│   ├── use_cases/         # Business use cases (AnalyzeBodyType, etc.)
│   └── services/          # Application services (Analytics, etc.)
├── infrastructure/        # External Dependencies
│   ├── ml_models/         # ML model implementations (YOLO, ResNet, SVM)
│   └── repositories/      # Data persistence implementations
└── presentation/          # User Interface
    ├── api/               # FastAPI routes and controllers
    └── dto/               # Data transfer objects for API
```

## ⚡ Quick Start

### 1. Installation

```bash
# Clone the repository
cd d:\Fitly\src\body-analysis-ai\BodyAnalysisAI

# Install dependencies
pip install -r requirements.txt

# Ensure YOLO model is available
# The yolov8m-pose.pt file should be in the project root
```

### 2. Start the Service

```bash
# Start development server
python run.py

# Or with uvicorn directly
uvicorn run:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/body/health
- **Service Info**: http://localhost:8000/

## 🔧 API Endpoints

### Core Analysis
- `POST /body/analyze` - Analyze body type from image
- `POST /body/validate` - Validate image quality
- `GET /body/history/{user_id}` - Get user's analysis history
- `GET /body/trends/{user_id}` - Get user's analysis trends

### Monitoring
- `GET /body/health` - Service health and model status
- `GET /` - Service information

## 📝 Usage Examples

### Analyze Body Type

```bash
curl -X POST "http://localhost:8000/body/analyze" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@body_image.jpg" \
     -F "user_id=user123" \
     -F "save_result=true"
```

**Response:**
```json
{
  "body_type": "hourglass",
  "confidence_score": 0.87,
  "body_ratios": {
    "shoulder_to_hip_ratio": 1.02,
    "waist_to_hip_ratio": 0.72,
    "shoulder_to_waist_ratio": 1.41,
    "torso_aspect_ratio": 1.85
  },
  "keypoints_detected": 17,
  "detection_confidence": 0.92,
  "result_id": "uuid-string"
}
```

### Validate Image

```bash
curl -X POST "http://localhost:8000/body/validate" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@body_image.jpg"
```

## 🤖 Machine Learning Pipeline

### 1. Image Preprocessing
- Resize and normalize images
- Validate image quality and format
- Ensure proper aspect ratios

### 2. Pose Keypoint Extraction
- YOLO v8 pose model for 17 COCO keypoints
- Confidence filtering and validation
- Coordinate normalization

### 3. Body Ratio Calculation
- Shoulder-to-hip ratio
- Waist-to-hip ratio  
- Shoulder-to-waist ratio
- Torso aspect ratio

### 4. Deep Learning Features
- ResNet50 backbone for image embeddings
- 512-dimensional feature vectors
- Transfer learning from ImageNet

### 5. Hybrid Classification
- Combine ratio features + DL embeddings
- SVM classifier with RBF kernel
- Probability estimates for confidence scores

