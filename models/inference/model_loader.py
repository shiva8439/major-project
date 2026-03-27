import torch
import torch.nn as nn
import torchvision.models as models
import os
from typing import Optional, Tuple, Dict, Any
import logging
import json
from ..training.model import create_model

logger = logging.getLogger(__name__)

class InferenceModelLoader:
    """Handles loading and managing AI models for inference"""
    
    def __init__(self):
        self.models = {}
        self.model_configs = {}
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
    
    def load_chest_xray_model(self, model_path: str, config_path: Optional[str] = None) -> nn.Module:
        """
        Load chest X-ray classification model
        
        Args:
            model_path: Path to the saved model file
            config_path: Path to model configuration file
            
        Returns:
            Loaded PyTorch model
        """
        try:
            # Load model configuration
            model_config = self._load_config(config_path, "chest_xray")
            
            # Create model
            model = create_model("chest_xray", **model_config)
            
            # Load trained weights if available
            if os.path.exists(model_path):
                checkpoint = torch.load(model_path, map_location=self.device)
                
                # Handle different checkpoint formats
                if 'model_state_dict' in checkpoint:
                    model.load_state_dict(checkpoint['model_state_dict'])
                elif 'state_dict' in checkpoint:
                    model.load_state_dict(checkpoint['state_dict'])
                else:
                    model.load_state_dict(checkpoint)
                
                logger.info(f"Loaded chest X-ray model from {model_path}")
                
                # Load metadata if available
                if 'metadata' in checkpoint:
                    self.model_configs['chest_xray'] = checkpoint['metadata']
            else:
                logger.warning(f"Model file not found at {model_path}. Using pretrained weights.")
            
            model = model.to(self.device)
            model.eval()
            
            self.models['chest_xray'] = model
            return model
            
        except Exception as e:
            logger.error(f"Error loading chest X-ray model: {e}")
            raise
    
    def load_brain_mri_model(self, model_path: str, config_path: Optional[str] = None) -> nn.Module:
        """
        Load brain MRI classification model
        
        Args:
            model_path: Path to the saved model file
            config_path: Path to model configuration file
            
        Returns:
            Loaded PyTorch model
        """
        try:
            # Load model configuration
            model_config = self._load_config(config_path, "brain_mri")
            
            # Create model
            model = create_model("brain_mri", **model_config)
            
            # Load trained weights if available
            if os.path.exists(model_path):
                checkpoint = torch.load(model_path, map_location=self.device)
                
                # Handle different checkpoint formats
                if 'model_state_dict' in checkpoint:
                    model.load_state_dict(checkpoint['model_state_dict'])
                elif 'state_dict' in checkpoint:
                    model.load_state_dict(checkpoint['state_dict'])
                else:
                    model.load_state_dict(checkpoint)
                
                logger.info(f"Loaded brain MRI model from {model_path}")
                
                # Load metadata if available
                if 'metadata' in checkpoint:
                    self.model_configs['brain_mri'] = checkpoint['metadata']
            else:
                logger.warning(f"Model file not found at {model_path}. Using pretrained weights.")
            
            model = model.to(self.device)
            model.eval()
            
            self.models['brain_mri'] = model
            return model
            
        except Exception as e:
            logger.error(f"Error loading brain MRI model: {e}")
            raise
    
    def _load_config(self, config_path: Optional[str], model_type: str) -> Dict[str, Any]:
        """Load model configuration from file or use defaults"""
        default_config = {
            "num_classes": 2,
            "pretrained": True
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                return {**default_config, **config.get(model_type, {})}
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config
    
    def get_model(self, model_type: str) -> Optional[nn.Module]:
        """
        Get loaded model by type
        
        Args:
            model_type: Type of model ('chest_xray' or 'brain_mri')
            
        Returns:
            Loaded model or None if not found
        """
        return self.models.get(model_type)
    
    def predict(self, model_type: str, input_tensor: torch.Tensor) -> Tuple[str, float, torch.Tensor]:
        """
        Make prediction using specified model
        
        Args:
            model_type: Type of model to use
            input_tensor: Preprocessed input tensor
            
        Returns:
            Tuple of (predicted_class, confidence_score, raw_output)
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
                class_names = ['Normal', 'Tumor']
            else:
                class_names = ['Class_0', 'Class_1']
            
            predicted_class = class_names[predicted.item()]
            confidence_score = confidence.item()
            
            return predicted_class, confidence_score, outputs
    
    def predict_batch(self, model_type: str, input_batch: torch.Tensor) -> Tuple[list, list, torch.Tensor]:
        """
        Make predictions for a batch of images
        
        Args:
            model_type: Type of model to use
            input_batch: Batch of preprocessed input tensors
            
        Returns:
            Tuple of (predicted_classes, confidence_scores, raw_outputs)
        """
        model = self.get_model(model_type)
        if model is None:
            raise ValueError(f"Model {model_type} not loaded")
        
        with torch.no_grad():
            input_batch = input_batch.to(self.device)
            outputs = model(input_batch)
            probabilities = torch.softmax(outputs, dim=1)
            confidence_scores, predicted_indices = torch.max(probabilities, 1)
            
            # Convert to class names
            if model_type == 'chest_xray':
                class_names = ['Normal', 'Pneumonia']
            elif model_type == 'brain_mri':
                class_names = ['Normal', 'Tumor']
            else:
                class_names = ['Class_0', 'Class_1']
            
            predicted_classes = [class_names[idx.item()] for idx in predicted_indices]
            confidence_scores = confidence_scores.cpu().numpy().tolist()
            
            return predicted_classes, confidence_scores, outputs
    
    def load_all_models(self, chest_model_path: str, brain_model_path: str, 
                       config_path: Optional[str] = None):
        """
        Load all available models
        
        Args:
            chest_model_path: Path to chest X-ray model
            brain_model_path: Path to brain MRI model
            config_path: Path to model configuration file
        """
        try:
            self.load_chest_xray_model(chest_model_path, config_path)
        except Exception as e:
            logger.error(f"Failed to load chest X-ray model: {e}")
        
        try:
            self.load_brain_mri_model(brain_model_path, config_path)
        except Exception as e:
            logger.error(f"Failed to load brain MRI model: {e}")
        
        logger.info(f"Loaded {len(self.models)} models successfully")
    
    def get_model_info(self, model_type: str) -> Dict[str, Any]:
        """
        Get information about a loaded model
        
        Args:
            model_type: Type of model
            
        Returns:
            Model information dictionary
        """
        model = self.get_model(model_type)
        if model is None:
            return {"error": f"Model {model_type} not loaded"}
        
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        
        info = {
            "model_type": model_type,
            "total_parameters": total_params,
            "trainable_parameters": trainable_params,
            "device": str(self.device),
            "model_class": model.__class__.__name__
        }
        
        # Add configuration if available
        if model_type in self.model_configs:
            info.update(self.model_configs[model_type])
        
        return info
    
    def warm_up_models(self):
        """Warm up models with dummy input to avoid first inference latency"""
        logger.info("Warming up models...")
        
        dummy_input = torch.randn(1, 3, 224, 224)
        
        for model_type in self.models.keys():
            try:
                _ = self.predict(model_type, dummy_input)
                logger.info(f"Model {model_type} warmed up successfully")
            except Exception as e:
                logger.error(f"Failed to warm up model {model_type}: {e}")

# Global model loader instance
model_loader = InferenceModelLoader()

# Model configuration template
MODEL_CONFIG_TEMPLATE = {
    "chest_xray": {
        "num_classes": 2,
        "pretrained": True,
        "class_names": ["Normal", "Pneumonia"],
        "input_size": [224, 224],
        "normalization": {
            "mean": [0.485, 0.456, 0.406],
            "std": [0.229, 0.224, 0.225]
        }
    },
    "brain_mri": {
        "num_classes": 2,
        "pretrained": True,
        "class_names": ["Normal", "Tumor"],
        "input_size": [224, 224],
        "normalization": {
            "mean": [0.485, 0.456, 0.406],
            "std": [0.229, 0.224, 0.225]
        }
    }
}

def save_model_config(config_path: str, config: Dict[str, Any] = None):
    """Save model configuration to file"""
    if config is None:
        config = MODEL_CONFIG_TEMPLATE
    
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info(f"Model configuration saved to {config_path}")
