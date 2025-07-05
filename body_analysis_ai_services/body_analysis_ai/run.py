from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import analyze

app = FastAPI(
    title="Body Analysis API",
    description="AI-powered body shape analysis service",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, prefix="/body", tags=["Body Analysis"])

@app.get("/")
def root():
    return {"message": "Body Analysis API running", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)