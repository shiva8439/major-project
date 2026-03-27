from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

from .routers import predict, chatbot
from .models.prediction import HealthCheck

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/backend.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Medical Diagnosis System",
    description="An AI-powered medical diagnosis system for analyzing medical images",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
allowed_origins = ["http://localhost:3000", "http://127.0.0.1:62577", "http://localhost:5173", "http://127.0.0.1:3000", "http://10.76.175.56:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
if os.path.exists(upload_dir):
    app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

# Include routers
app.include_router(predict.router)
app.include_router(chatbot.router)

# Health check endpoint
@app.get("/", response_model=HealthCheck)
async def health_check():
    """
    Health check endpoint to verify the API is running
    
    Returns:
        Health status with timestamp and version
    """
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0"
    )

@app.get("/api/health")
async def api_health():
    """
    API health check endpoint
    
    Returns:
        API health status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "endpoints": {
            "predict": "/api/predict",
            "chat": "/api/chat",
            "history": "/api/history",
            "health": "/api/health"
        }
    }

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.now()
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs(upload_dir, exist_ok=True)
    
    logger.info("AI Medical Diagnosis System started successfully")
    logger.info(f"Documentation available at: http://localhost:8000/docs")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("AI Medical Diagnosis System shutting down")

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
