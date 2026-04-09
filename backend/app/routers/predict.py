from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
import uuid
import io
from PIL import Image
import numpy as np
import torch

from app.database.models import Prediction, get_db
from app.utils.image_utils import validate_image, preprocess_image, save_uploaded_image, load_image_for_display
from app.utils.config import UPLOAD_DIR, HEATMAP_DIR
from app.models.model_loader import model_loader
from app.models.gradcam import get_gradcam
from app.models.model_loader import CLASS_LABELS

router = APIRouter()

@router.post("/predict")
async def predict_medical_image(
    image: UploadFile = File(...),
    image_type: str = Form(...),  # chest_xray or brain_mri
    db: Session = Depends(get_db)
):
    """
    Predict medical image diagnosis
    - Upload image (jpg/png)
    - Select type: chest_xray or brain_mri
    """
    if image_type not in ["chest_xray", "brain_mri"]:
        raise HTTPException(400, "Invalid image_type")
    
    # Read image bytes
    image_bytes = await image.read()
    
    # Validate
    if not validate_image(image_bytes):
        raise HTTPException(400, "Invalid image format")
    
    # Save original
    filename = f"{uuid.uuid4()}_{image.filename}"
    original_path = save_uploaded_image(image_bytes, filename)
    
    # Load model if not loaded
    model_key = image_type
    if model_key not in model_loader.models:
        from app.utils.config import CHEST_XRAY_MODEL_PATH, BRAIN_MRI_MODEL_PATH
        if image_type == "chest_xray":
            model_loader.load_model(CHEST_XRAY_MODEL_PATH, model_key)
        else:
            model_loader.load_model(BRAIN_MRI_MODEL_PATH, model_key)
    
    # Preprocess
    pil_image = Image.open(io.BytesIO(image_bytes))
    img_tensor = torch.tensor(preprocess_image(pil_image))
    
    # Predict
    pred_label, confidence = model_loader.predict(model_key, img_tensor)
    pred_idx = CLASS_LABELS[model_key].index(pred_label)
    
    # Generate heatmap
    heatmap_path = get_gradcam(model_key, img_tensor, pred_idx, original_path)
    
    # Save to DB
    db_prediction = Prediction(
        image_type=image_type,
        prediction=pred_label,
        confidence=confidence,
        original_image_path=original_path,
        heatmap_path=heatmap_path
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    
    # Response
    return {
        "id": db_prediction.id,
        "image_type": image_type,
        "prediction": pred_label,
        "confidence": round(confidence * 100, 2),
        "heatmap_url": f"/api/heatmap/{db_prediction.id}",
        "message": f"Predicted: {pred_label} ({confidence:.2%} confidence)"
    }

@router.get("/heatmap/{prediction_id}")
async def get_heatmap(prediction_id: int, db: Session = Depends(get_db)):
    """Serve heatmap image"""
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not prediction or not prediction.heatmap_path:
        raise HTTPException(404, "Heatmap not found")
    
    try:
        return FileResponse(prediction.heatmap_path, media_type="image/jpeg")
    except FileNotFoundError:
        raise HTTPException(404, "Heatmap file not found")
