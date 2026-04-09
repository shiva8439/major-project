from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import desc

from app.database.models import get_db, Prediction
from app.utils.config import UPLOAD_DIR, HEATMAP_DIR

router = APIRouter()

@router.get("/history")
def get_prediction_history(db: Session = Depends(get_db)) -> List[dict]:
    """Get prediction history (latest first)"""
    predictions = db.query(Prediction).order_by(desc(Prediction.timestamp)).limit(50).all()
    return [
        {
            "id": p.id,
            "image_type": p.image_type,
            "prediction": p.prediction,
            "confidence": round(p.confidence * 100, 2),
            "timestamp": p.timestamp.isoformat()
        }
        for p in predictions
    ]

from fastapi.responses import FileResponse
from pathlib import Path

@router.get("/heatmap/{prediction_id}")
def get_heatmap(prediction_id: int, db: Session = Depends(get_db)):
    """Serve heatmap image for prediction ID"""
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not prediction:
        raise HTTPException(404, "Prediction not found")
    
    if not prediction.heatmap_path or not Path(prediction.heatmap_path).exists():
        raise HTTPException(404, "Heatmap not available")
    
    return FileResponse(prediction.heatmap_path, media_type="image/jpeg", filename="heatmap.jpg")
