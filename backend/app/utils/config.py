from pathlib import Path
from typing import Tuple, Dict

# Project root
BACKEND_DIR = Path(__file__).parent.parent

# Model paths - update with actual .pth files
MODELS_DIR = BACKEND_DIR / "models"
CHEST_XRAY_MODEL_PATH = MODELS_DIR / "chest_xray_model.pth"
BRAIN_MRI_MODEL_PATH = MODELS_DIR / "brain_mri_model.pth"

# ImageNet normalization for ResNet
MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]

IMG_SIZE = (224, 224)

# Class labels
CLASS_LABELS = {
    "chest_xray": ["Normal", "Pneumonia", "COVID-19", "Tuberculosis"],
    "brain_mri": ["Normal", "Glioma", "Meningioma", "Pituitary Tumor", "Metastasis"]
}

# API config
BACKEND_HOST = "http://localhost:8000"
UPLOAD_DIR = BACKEND_DIR / "uploads"
HEATMAP_DIR = BACKEND_DIR / "heatmaps"

# Create dirs
for directory in [MODELS_DIR, UPLOAD_DIR, HEATMAP_DIR]:
    directory.mkdir(exist_ok=True)
