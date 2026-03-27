import torch
import torch.nn as nn
import torchvision.models as models
import os
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class ModelLoader:
    """Handles loading and managing AI models"""
    
    def __init__(self):
        self.models = {}
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
    
    def load_chest_xray_model(self, model_path: str) -> nn.Module:
        """
        Load chest X-ray classification model
        
        Args:
            model_path: Path to the saved model file
            
        Returns:
            Loaded PyTorch model
        """
        try:
            # Load ResNet50 pretrained model
            model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
            
            # Modify final layer for binary classification (Normal/Pneumonia)
            num_features = model.fc.in_features
            model.fc = nn.Sequential(
                nn.Dropout(0.5),
                nn.Linear(num_features, 2)  # 2 classes: Normal, Pneumonia
            )
            
            # Load trained weights if available
            if os.path.exists(model_path):
                checkpoint = torch.load(model_path, map_location=self.device)
                model.load_state_dict(checkpoint['model_state_dict'])
                logger.info(f"Loaded chest X-ray model from {model_path}")
            else:
                logger.warning(f"Model file not found at {model_path}. Using pretrained weights.")
            
            model = model.to(self.device)
            model.eval()
            
            self.models['chest_xray'] = model
            return model
            
        except Exception as e:
            logger.error(f"Error loading chest X-ray model: {e}")
            raise
    
    def load_brain_mri_model(self, model_path: str) -> nn.Module:
        """
        Load brain MRI classification model
        
        Args:
            model_path: Path to the saved model file
            
        Returns:
            Loaded PyTorch model
        """
        try:
            # Load EfficientNet-B0 pretrained model
            model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
            
            # Modify final layer for 4-class classification (glioma, meningioma, notumor, pituitary)
            num_features = model.classifier[1].in_features
            model.classifier[1] = nn.Sequential(
                nn.Dropout(0.5),
                nn.Linear(num_features, 4)  # 4 classes: glioma, meningioma, notumor, pituitary
            )
            
            # Load trained weights if available
            if os.path.exists(model_path):
                checkpoint = torch.load(model_path, map_location=self.device)
                model.load_state_dict(checkpoint['model_state_dict'])
                logger.info(f"Loaded brain MRI model from {model_path}")
            else:
                logger.warning(f"Model file not found at {model_path}. Using pretrained weights.")
            
            model = model.to(self.device)
            model.eval()
            
            self.models['brain_mri'] = model
            return model
            
        except Exception as e:
            logger.error(f"Error loading brain MRI model: {e}")
            raise
    
    def get_model(self, model_type: str) -> Optional[nn.Module]:
        """
        Get loaded model by type
        
        Args:
            model_type: Type of model ('chest_xray' or 'brain_mri')
            
        Returns:
            Loaded model or None if not found
        """
        return self.models.get(model_type)
    
    def predict(self, model_type: str, input_tensor: torch.Tensor) -> Tuple[str, float]:
        """
        Make prediction using specified model
        
        Args:
            model_type: Type of model to use
            input_tensor: Preprocessed input tensor
            
        Returns:
            Tuple of (predicted_class, confidence_score)
        """
        model = self.get_model(model_type)
        if model is None:
            raise ValueError(f"Model {model_type} not loaded")
        
        with torch.no_grad():
            input_tensor = input_tensor.to(self.device)
            outputs = model(input_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
            
            # Convert to class names
            if model_type == 'chest_xray':
                class_names = ['Normal', 'Pneumonia']
            elif model_type == 'brain_mri':
                class_names = ['glioma', 'meningioma', 'notumor', 'pituitary']
            else:
                class_names = ['Class_0', 'Class_1']
            
            predicted_class = class_names[predicted.item()]
            confidence_score = confidence.item()
            
            return predicted_class, confidence_score
    
    def load_all_models(self, chest_model_path: str, brain_model_path: str):
        """
        Load all available models
        
        Args:
            chest_model_path: Path to chest X-ray model
            brain_model_path: Path to brain MRI model
        """
        try:
            self.load_chest_xray_model(chest_model_path)
        except Exception as e:
            logger.error(f"Failed to load chest X-ray model: {e}")
        
        try:
            self.load_brain_mri_model(brain_model_path)
        except Exception as e:
            logger.error(f"Failed to load brain MRI model: {e}")
        
        logger.info(f"Loaded {len(self.models)} models successfully")

# Global model loader instance
model_loader = ModelLoader()
