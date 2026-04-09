import cv2
import numpy as np
from PIL import Image
from typing import Tuple
import os
from pathlib import Path
from .config import UPLOAD_DIR, IMG_SIZE, MEAN, STD

import io

def validate_image(image_bytes: bytes) -> bool:
    """Validate if bytes are valid image"""
    try:
        Image.open(io.BytesIO(image_bytes)).verify()
        return True
    except:
        return False

def preprocess_image(image: Image.Image) -> np.ndarray:
    """Preprocess image for model input"""
    # Resize
    image = image.resize(IMG_SIZE)
    
    # Convert to RGB if needed
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # To numpy array
    img_array = np.array(image, dtype=np.float32)
    
    # Normalize
    for c in range(3):
        img_array[:, :, c] = (img_array[:, :, c] / 255.0 - MEAN[c]) / STD[c]
    
    # Transpose to CHW and add batch dim
    img_array = np.transpose(img_array, (2, 0, 1))
    img_array = np.expand_dims(img_array, axis=0)
    
    return img_array

def save_uploaded_image(image_bytes: bytes, filename: str) -> str:
    """Save uploaded image"""
    path = UPLOAD_DIR / filename
    with open(path, "wb") as f:
        f.write(image_bytes)
    return str(path)

def load_image_for_display(image_path: str) -> Image.Image:
    """Load image for heatmap overlay"""
    return Image.open(image_path).convert('RGB')
