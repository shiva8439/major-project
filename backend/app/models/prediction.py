from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class PredictionRequest(BaseModel):
    image_type: str = Field(..., description="Type of medical image (chest_xray, brain_mri)")
    
class PredictionResponse(BaseModel):
    prediction: str = Field(..., description="Predicted condition")
    confidence: float = Field(..., description="Confidence score (0-1)")
    confidence_percentage: float = Field(..., description="Confidence score as percentage")
    heatmap_url: Optional[str] = Field(None, description="URL to Grad-CAM heatmap")
    processing_time: float = Field(..., description="Time taken for processing in seconds")
    model_type: str = Field(..., description="Type of model used")
    success: bool = Field(default=True, description="Whether prediction was successful")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            "datetime": lambda v: v.isoformat()
        }

class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message to the chatbot")
    language: str = Field(default="en", description="Language preference (en, hi)")

class ChatResponse(BaseModel):
    response: str = Field(..., description="Chatbot's response")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            "datetime": lambda v: v.isoformat()
        }

class HistoryItem(BaseModel):
    id: int
    image_type: str
    prediction: str
    confidence: float
    timestamp: datetime
    heatmap_url: Optional[str] = None
    
    class Config:
        json_encoders = {
            "datetime": lambda v: v.isoformat()
        }

class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    version: str
    
    class Config:
        json_encoders = {
            "datetime": lambda v: v.isoformat()
        }
