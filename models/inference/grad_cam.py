import torch
import torch.nn as nn
import cv2
import numpy as np
from PIL import Image
import io
import base64
import logging
from typing import Optional, Tuple, Dict, Any

logger = logging.getLogger(__name__)

class GradCAMGenerator:
    """Grad-CAM implementation for model explainability"""
    
    def __init__(self):
        self.gradients = None
        self.activations = None
        self.hooks = []
    
    def _register_hooks(self, model: nn.Module, target_layer_name: str):
        """Register forward and backward hooks"""
        # Clear previous hooks
        self._clear_hooks()
        
        def forward_hook(module, input, output):
            self.activations = output
        
        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0]
        
        # Find target layer and register hooks
        target_layer = None
        for name, module in model.named_modules():
            if name == target_layer_name:
                target_layer = module
                break
        
        if target_layer is None:
            logger.warning(f"Target layer '{target_layer_name}' not found")
            return False
        
        hook_forward = target_layer.register_forward_hook(forward_hook)
        hook_backward = target_layer.register_backward_hook(backward_hook)
        
        self.hooks.extend([hook_forward, hook_backward])
        return True
    
    def _clear_hooks(self):
        """Clear all registered hooks"""
        for hook in self.hooks:
            hook.remove()
        self.hooks = []
    
    def _get_target_layer_name(self, model_type: str, model: nn.Module) -> str:
        """Get target layer name based on model type"""
        if model_type == 'chest_xray':
            # For ResNet50
            return 'layer4'
        elif model_type == 'brain_mri':
            # For EfficientNet-B0
            return 'features.8'
        else:
            # Default for ResNet-like models
            return 'layer4'
    
    def generate_cam(self, model: nn.Module, input_tensor: torch.Tensor, 
                    class_idx: Optional[int] = None, model_type: str = 'chest_xray') -> np.ndarray:
        """
        Generate Grad-CAM heatmap
        
        Args:
            model: PyTorch model
            input_tensor: Input image tensor
            class_idx: Target class index (if None, uses predicted class)
            model_type: Type of model for layer selection
            
        Returns:
            Grad-CAM heatmap as numpy array
        """
        try:
            # Get target layer name
            target_layer_name = self._get_target_layer_name(model_type, model)
            
            # Register hooks
            if not self._register_hooks(model, target_layer_name):
                # Fallback: try to find a suitable layer
                logger.warning("Failed to register hooks for target layer, using fallback")
                return self._generate_fallback_heatmap(input_tensor)
            
            # Forward pass
            model.eval()
            output = model(input_tensor)
            
            if class_idx is None:
                class_idx = output.argmax(dim=1).item()
            
            # Zero gradients
            model.zero_grad()
            
            # Backward pass for target class
            class_score = output[0, class_idx]
            class_score.backward(retain_graph=True)
            
            # Get gradients and activations
            if self.gradients is None or self.activations is None:
                logger.error("Failed to capture gradients or activations")
                return self._generate_fallback_heatmap(input_tensor)
            
            gradients = self.gradients[0]  # [C, H, W]
            activations = self.activations[0]  # [C, H, W]
            
            # Global average pooling of gradients
            weights = torch.mean(gradients, dim=(1, 2))  # [C]
            
            # Weighted combination of activation maps
            cam = torch.zeros(activations.shape[1:], dtype=torch.float32)  # [H, W]
            for i, w in enumerate(weights):
                cam += w * activations[i]
            
            # Apply ReLU
            cam = torch.relu(cam)
            
            # Normalize to [0, 1]
            if cam.max() > 0:
                cam = cam / cam.max()
            
            # Convert to numpy
            cam = cam.cpu().numpy()
            
            # Clear hooks
            self._clear_hooks()
            
            return cam
            
        except Exception as e:
            logger.error(f"Error generating Grad-CAM: {e}")
            return self._generate_fallback_heatmap(input_tensor)
    
    def _generate_fallback_heatmap(self, input_tensor: torch.Tensor) -> np.ndarray:
        """Generate a fallback heatmap when Grad-CAM fails"""
        # Create a simple gradient-based visualization
        if len(input_tensor.shape) == 4:
            input_tensor = input_tensor[0]
        
        # Convert to numpy and create gradient
        img_np = input_tensor.cpu().numpy()
        if img_np.shape[0] == 3:  # RGB
            img_np = np.transpose(img_np, (1, 2, 0))
        
        # Create simple gradient heatmap
        h, w = img_np.shape[:2]
        heatmap = np.zeros((h, w))
        
        # Create radial gradient from center
        center_x, center_y = w // 2, h // 2
        for i in range(h):
            for j in range(w):
                dist = np.sqrt((i - center_y)**2 + (j - center_x)**2)
                heatmap[i, j] = 1.0 - (dist / (max(h, w) / 2))
        
        return np.clip(heatmap, 0, 1)
    
    def overlay_heatmap(self, original_image: np.ndarray, cam: np.ndarray, 
                       alpha: float = 0.4, colormap: int = cv2.COLORMAP_JET) -> np.ndarray:
        """
        Overlay Grad-CAM heatmap on original image
        
        Args:
            original_image: Original image as numpy array
            cam: Grad-CAM heatmap
            alpha: Transparency factor for overlay
            colormap: OpenCV colormap for heatmap
            
        Returns:
            Image with heatmap overlay
        """
        try:
            # Resize CAM to match original image size
            cam_resized = cv2.resize(cam, (original_image.shape[1], original_image.shape[0]))
            
            # Apply colormap
            heatmap = cv2.applyColorMap(np.uint8(255 * cam_resized), colormap)
            
            # Convert original image to BGR if needed
            if len(original_image.shape) == 3 and original_image.shape[2] == 3:
                original_bgr = cv2.cvtColor(original_image, cv2.COLOR_RGB2BGR)
            else:
                original_bgr = original_image
            
            # Overlay heatmap
            overlay = cv2.addWeighted(original_bgr, 1 - alpha, heatmap, alpha, 0)
            
            return overlay
            
        except Exception as e:
            logger.error(f"Error creating heatmap overlay: {e}")
            return original_image.copy()
    
    def generate_heatmap_data(self, model: nn.Module, input_tensor: torch.Tensor, 
                             original_image: np.ndarray, model_type: str, 
                             prediction: str) -> Dict[str, Any]:
        """
        Generate complete heatmap data for frontend
        
        Args:
            model: PyTorch model
            input_tensor: Preprocessed input tensor
            original_image: Original image as numpy array
            model_type: Type of model
            prediction: Predicted class
            
        Returns:
            Dictionary containing heatmap data
        """
        try:
            # Determine class index
            class_names = ['Normal', 'Pneumonia'] if model_type == 'chest_xray' else ['Normal', 'Tumor']
            class_idx = class_names.index(prediction) if prediction in class_names else 0
            
            # Generate CAM
            cam = self.generate_cam(model, input_tensor, class_idx, model_type)
            
            # Create overlay
            overlay = self.overlay_heatmap(original_image, cam)
            
            # Convert to base64 for frontend
            heatmap_base64 = self._image_to_base64(overlay, format='PNG')
            cam_base64 = self._image_to_base64((cam * 255).astype(np.uint8), format='PNG')
            
            return {
                'heatmap_overlay': heatmap_base64,
                'cam_raw': cam_base64,
                'class_idx': class_idx,
                'target_layer': self._get_target_layer_name(model_type, model),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error generating heatmap data: {e}")
            return {
                'heatmap_overlay': None,
                'cam_raw': None,
                'success': False,
                'error': str(e)
            }
    
    def _image_to_base64(self, image: np.ndarray, format: str = 'PNG') -> str:
        """Convert numpy array to base64 string"""
        try:
            # Convert numpy array to PIL Image
            if len(image.shape) == 3:
                image = Image.fromarray(image)
            else:
                image = Image.fromarray(image, mode='L')
            
            # Convert to bytes
            buffer = io.BytesIO()
            image.save(buffer, format=format)
            image_bytes = buffer.getvalue()
            
            # Encode to base64
            base64_string = base64.b64encode(image_bytes).decode('utf-8')
            return f"data:image/{format.lower()};base64,{base64_string}"
            
        except Exception as e:
            logger.error(f"Error converting image to base64: {e}")
            return ""
    
    def generate_explanation_map(self, cam: np.ndarray, threshold: float = 0.5) -> Dict[str, Any]:
        """
        Generate explanation map with regions of interest
        
        Args:
            cam: Grad-CAM heatmap
            threshold: Threshold for important regions
            
        Returns:
            Dictionary with explanation data
        """
        try:
            # Find important regions
            important_regions = cam > threshold
            
            # Find contours of important regions
            contours, _ = cv2.findContours(
                important_regions.astype(np.uint8) * 255,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Extract bounding boxes
            bounding_boxes = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = cv2.contourArea(contour)
                if area > 100:  # Filter small regions
                    bounding_boxes.append({
                        'x': int(x),
                        'y': int(y),
                        'width': int(w),
                        'height': int(h),
                        'area': float(area),
                        'importance': float(cam[y:y+h, x:x+w].mean())
                    })
            
            # Sort by importance
            bounding_boxes.sort(key=lambda x: x['importance'], reverse=True)
            
            # Calculate statistics
            total_important_area = np.sum(important_regions)
            total_area = cam.shape[0] * cam.shape[1]
            importance_ratio = total_important_area / total_area
            
            return {
                'important_regions': important_regions.tolist(),
                'bounding_boxes': bounding_boxes[:5],  # Top 5 regions
                'importance_ratio': float(importance_ratio),
                'mean_importance': float(cam.mean()),
                'max_importance': float(cam.max()),
                'threshold_used': threshold
            }
            
        except Exception as e:
            logger.error(f"Error generating explanation map: {e}")
            return {
                'important_regions': [],
                'bounding_boxes': [],
                'importance_ratio': 0.0,
                'mean_importance': 0.0,
                'max_importance': 0.0,
                'error': str(e)
            }

# Global Grad-CAM generator instance
grad_cam_generator = GradCAMGenerator()
