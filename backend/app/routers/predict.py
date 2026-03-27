from fastapi import APIRouter, UploadFile, File, Form ,HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import time
import os
import uuid
from typing import Optional

from ..models.prediction import PredictionRequest, PredictionResponse
from ..database import get_db, PredictionHistory
from ..utils.image_processor import ImageProcessor
from ..utils.model_loader import model_loader
from ..utils.grad_cam import get_grad_cam_for_model

router = APIRouter(prefix="/api", tags=["prediction"])
image_processor = ImageProcessor()


@router.post("/predict", response_model=PredictionResponse)
async def predict_medical_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    image_type: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Analyze medical image and return prediction with Grad-CAM visualization
    
    Args:
        file: Uploaded medical image file
        image_type: Type of image (chest_xray, brain_mri)
        db: Database session
        
    Returns:
        Prediction result with confidence and heatmap
    """
    # Validate image type
    if image_type not in ["chest_xray", "brain_mri"]:
        raise HTTPException(status_code=400, detail="Invalid image type. Must be 'chest_xray' or 'brain_mri'")
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Check file size (max 10MB)
    max_size = int(os.getenv("MAX_FILE_SIZE", 10485760))
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > max_size:
        raise HTTPException(status_code=400, detail=f"File too large. Maximum size is {max_size//1024//1024}MB")
    
    # Validate image
    if not image_processor.validate_image(content):
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    start_time = time.time()
    
    # 🔥 Debug print
    print("Prediction API hit")
    print(f"Image type: {image_type}")
    print(f"File size: {file_size} bytes")
    
    try:
        # Preprocess image
        input_tensor, original_image = image_processor.preprocess_image(content)
        
        # Get prediction
        prediction, confidence = model_loader.predict(image_type, input_tensor)
        
        # Generate Grad-CAM heatmap
        heatmap, overlay = get_grad_cam_for_model(
            image_type, 
            model_loader.get_model(image_type),
            input_tensor,
            original_image
        )
        
        # Convert overlay to base64 for frontend
        heatmap_base64 = image_processor.image_to_base64(overlay, format='PNG')
        
        # Save images to uploads directory
        upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        original_filename = f"{file_id}_original.png"
        heatmap_filename = f"{file_id}_heatmap.png"
        
        # Save files
        original_path = os.path.join(upload_dir, original_filename)
        heatmap_path = os.path.join(upload_dir, heatmap_filename)
        
        # Save original image
        from PIL import Image
        Image.fromarray(original_image).save(original_path)
        
        # Save heatmap
        Image.fromarray(overlay).save(heatmap_path)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Create response
        response = PredictionResponse(
            prediction=prediction,
            confidence=confidence,
            confidence_percentage=round(confidence * 100, 2),
            heatmap_url=f"/api/heatmap/{file_id}",
            processing_time=processing_time,
            model_type=image_type
        )
        
        # Save to database in background
        background_tasks.add_task(
            save_prediction_to_db,
            db=db,
            image_type=image_type,
            prediction=prediction,
            confidence=confidence,
            heatmap_path=heatmap_path,
            processing_time=processing_time
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.get("/heatmap/{file_id}")
async def get_heatmap(file_id: str):
    """
    Serve heatmap image
    
    Args:
        file_id: Unique identifier for the heatmap
        
    Returns:
        Heatmap image file
    """
    upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
    heatmap_filename = f"{file_id}_heatmap.png"
    heatmap_path = os.path.join(upload_dir, heatmap_filename)
    
    if not os.path.exists(heatmap_path):
        raise HTTPException(status_code=404, detail="Heatmap not found")
    
    from fastapi.responses import FileResponse
    return FileResponse(heatmap_path, media_type="image/png")

@router.get("/history")
async def get_prediction_history(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get prediction history
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of prediction history
    """
    try:
        history = db.query(PredictionHistory)\
                   .order_by(PredictionHistory.timestamp.desc())\
                   .offset(skip)\
                   .limit(limit)\
                   .all()
        
        return [
            {
                "id": item.id,
                "image_type": item.image_type,
                "prediction": item.prediction,
                "confidence": item.confidence,
                "timestamp": item.timestamp,
                "processing_time": item.processing_time
            }
            for item in history
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")

def save_prediction_to_db(
    db: Session,
    image_type: str,
    prediction: str,
    confidence: float,
    heatmap_path: str,
    processing_time: float
):
    """
    Save prediction result to database
    
    Args:
        db: Database session
        image_type: Type of medical image
        prediction: Predicted condition
        confidence: Confidence score
        heatmap_path: Path to heatmap file
        processing_time: Processing time in seconds
    """
    try:
        history_item = PredictionHistory(
            image_type=image_type,
            prediction=prediction,
            confidence=confidence,
            heatmap_path=heatmap_path,
            processing_time=processing_time
        )
        db.add(history_item)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Failed to save to database: {e}")
