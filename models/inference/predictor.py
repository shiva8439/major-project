import torch
import torch.nn as nn
import torchvision.transforms as transforms
import numpy as np
from PIL import Image
import cv2
import io
import logging
from typing import Tuple, Dict, Any, Optional
import time

from .model_loader import model_loader
from .grad_cam import GradCAMGenerator

logger = logging.getLogger(__name__)

class MedicalImagePredictor:
    """Main predictor class for medical image analysis"""
    
    def __init__(self):
        self.transform = self._get_inference_transform()
        self.grad_cam_generator = GradCAMGenerator()
        self.prediction_cache = {}
    
    def _get_inference_transform(self):
        """Get image transformation for inference"""
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    
    def preprocess_image(self, image_data: bytes) -> Tuple[torch.Tensor, np.ndarray]:
        """
        Preprocess uploaded image for model inference
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Tuple of (processed_tensor, original_image_array)
        """
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Store original image as numpy array
            original_image = np.array(image)
            
            # Apply transformations
            processed_image = self.transform(image)
            
            # Add batch dimension
            processed_image = processed_image.unsqueeze(0)
            
            return processed_image, original_image
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            raise ValueError(f"Invalid image data: {e}")
    
    def predict(self, image_data: bytes, model_type: str, 
               generate_heatmap: bool = True) -> Dict[str, Any]:
        """
        Make prediction on medical image
        
        Args:
            image_data: Raw image bytes
            model_type: Type of model to use ('chest_xray' or 'brain_mri')
            generate_heatmap: Whether to generate Grad-CAM heatmap
            
        Returns:
            Dictionary containing prediction results
        """
        start_time = time.time()
        
        try:
            # Validate model type
            if model_type not in ['chest_xray', 'brain_mri']:
                raise ValueError(f"Invalid model type: {model_type}")
            
            # Check if model is loaded
            model = model_loader.get_model(model_type)
            if model is None:
                raise ValueError(f"Model {model_type} not loaded")
            
            # Preprocess image
            input_tensor, original_image = self.preprocess_image(image_data)
            
            # Make prediction
            prediction, confidence, raw_output = model_loader.predict(model_type, input_tensor)
            
            # Generate heatmap if requested
            heatmap_data = None
            if generate_heatmap:
                try:
                    heatmap_data = self.grad_cam_generator.generate_heatmap(
                        model, input_tensor, original_image, model_type, prediction
                    )
                except Exception as e:
                    logger.warning(f"Failed to generate heatmap: {e}")
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Prepare result
            result = {
                'prediction': prediction,
                'confidence': confidence,
                'confidence_percentage': round(confidence * 100, 2),
                'processing_time': round(processing_time, 3),
                'model_type': model_type,
                'image_shape': original_image.shape,
                'success': True
            }
            
            # Add heatmap data if generated
            if heatmap_data:
                result.update({
                    'heatmap_generated': True,
                    'heatmap_data': heatmap_data
                })
            else:
                result['heatmap_generated'] = False
            
            # Log prediction
            logger.info(f"Prediction completed: {prediction} ({confidence:.3f}) in {processing_time:.3f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {
                'prediction': None,
                'confidence': 0.0,
                'confidence_percentage': 0.0,
                'processing_time': time.time() - start_time,
                'model_type': model_type,
                'success': False,
                'error': str(e)
            }
    
    def predict_batch(self, image_data_list: list, model_type: str) -> Dict[str, Any]:
        """
        Make predictions on multiple images
        
        Args:
            image_data_list: List of raw image bytes
            model_type: Type of model to use
            
        Returns:
            Dictionary containing batch prediction results
        """
        start_time = time.time()
        
        try:
            # Validate inputs
            if not image_data_list:
                raise ValueError("Empty image list provided")
            
            if model_type not in ['chest_xray', 'brain_mri']:
                raise ValueError(f"Invalid model type: {model_type}")
            
            # Check if model is loaded
            model = model_loader.get_model(model_type)
            if model is None:
                raise ValueError(f"Model {model_type} not loaded")
            
            # Preprocess all images
            processed_images = []
            original_images = []
            
            for image_data in image_data_list:
                input_tensor, original_image = self.preprocess_image(image_data)
                processed_images.append(input_tensor)
                original_images.append(original_image)
            
            # Stack images for batch processing
            batch_tensor = torch.cat(processed_images, dim=0)
            
            # Make batch prediction
            predictions, confidences, raw_outputs = model_loader.predict_batch(model_type, batch_tensor)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Prepare results
            results = []
            for i, (pred, conf) in enumerate(zip(predictions, confidences)):
                results.append({
                    'prediction': pred,
                    'confidence': conf,
                    'confidence_percentage': round(conf * 100, 2),
                    'image_shape': original_images[i].shape
                })
            
            return {
                'predictions': results,
                'batch_size': len(image_data_list),
                'processing_time': round(processing_time, 3),
                'model_type': model_type,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Batch prediction failed: {e}")
            return {
                'predictions': [],
                'batch_size': len(image_data_list),
                'processing_time': time.time() - start_time,
                'model_type': model_type,
                'success': False,
                'error': str(e)
            }
    
    def get_prediction_explanation(self, prediction_result: Dict[str, Any]) -> str:
        """
        Generate human-readable explanation of prediction
        
        Args:
            prediction_result: Result from predict method
            
        Returns:
            Human-readable explanation
        """
        if not prediction_result.get('success', False):
            return f"Prediction failed: {prediction_result.get('error', 'Unknown error')}"
        
        prediction = prediction_result['prediction']
        confidence = prediction_result['confidence_percentage']
        model_type = prediction_result['model_type']
        
        if model_type == 'chest_xray':
            if prediction == 'Normal':
                return f"The chest X-ray appears **Normal** with {confidence}% confidence. No signs of pneumonia detected."
            else:
                return f"The chest X-ray shows signs of **Pneumonia** with {confidence}% confidence. Medical consultation recommended."
        
        elif model_type == 'brain_mri':
            if prediction == 'Normal':
                return f"The brain MRI appears **Normal** with {confidence}% confidence. No signs of tumor detected."
            else:
                return f"The brain MRI shows signs of **Tumor** with {confidence}% confidence. Immediate medical consultation recommended."
        
        else:
            return f"Prediction: {prediction} with {confidence}% confidence."
    
    def validate_prediction(self, prediction_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate prediction result and add quality metrics
        
        Args:
            prediction_result: Result from predict method
            
        Returns:
            Validated result with quality metrics
        """
        if not prediction_result.get('success', False):
            return prediction_result
        
        confidence = prediction_result['confidence']
        processing_time = prediction_result['processing_time']
        
        # Quality checks
        quality_metrics = {
            'high_confidence': confidence >= 0.8,
            'medium_confidence': 0.5 <= confidence < 0.8,
            'low_confidence': confidence < 0.5,
            'fast_processing': processing_time < 2.0,
            'slow_processing': processing_time >= 5.0
        }
        
        # Overall quality score
        quality_score = 0
        if quality_metrics['high_confidence']:
            quality_score += 40
        elif quality_metrics['medium_confidence']:
            quality_score += 25
        else:
            quality_score += 10
        
        if quality_metrics['fast_processing']:
            quality_score += 20
        elif not quality_metrics['slow_processing']:
            quality_score += 15
        else:
            quality_score += 5
        
        # Add heatmap bonus
        if prediction_result.get('heatmap_generated', False):
            quality_score += 20
        
        # Add model info bonus
        if prediction_result.get('model_type'):
            quality_score += 20
        
        quality_metrics['overall_score'] = min(100, quality_score)
        quality_metrics['quality_level'] = self._get_quality_level(quality_score)
        
        prediction_result['quality_metrics'] = quality_metrics
        
        return prediction_result
    
    def _get_quality_level(self, score: int) -> str:
        """Get quality level based on score"""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Poor"

# Global predictor instance
predictor = MedicalImagePredictor()

def initialize_models(chest_model_path: str, brain_model_path: str, config_path: Optional[str] = None):
    """
    Initialize all models for inference
    
    Args:
        chest_model_path: Path to chest X-ray model
        brain_model_path: Path to brain MRI model
        config_path: Path to model configuration file
    """
    try:
        model_loader.load_all_models(chest_model_path, brain_model_path, config_path)
        model_loader.warm_up_models()
        logger.info("All models initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize models: {e}")
        return False
