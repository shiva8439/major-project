import torch
import torch.nn as nn
import cv2
import numpy as np
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class GradCAM:
    """
    Grad-CAM implementation for model explainability
    """
    
    def __init__(self, model: nn.Module, target_layer: str):
        """
        Initialize Grad-CAM
        
        Args:
            model: PyTorch model
            target_layer: Name of the target layer for visualization
        """
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        # Register hooks
        self._register_hooks()
    
    def _register_hooks(self):
        """Register forward and backward hooks"""
        def forward_hook(module, input, output):
            self.activations = output
        
        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0]
        
        # Find target layer and register hooks
        for name, module in self.model.named_modules():
            if name == self.target_layer:
                module.register_forward_hook(forward_hook)
                module.register_backward_hook(backward_hook)
                break
        else:
            logger.warning(f"Target layer '{self.target_layer}' not found")
    
    def generate_cam(self, input_tensor: torch.Tensor, class_idx: Optional[int] = None) -> np.ndarray:
        """
        Generate Grad-CAM heatmap
        
        Args:
            input_tensor: Input image tensor
            class_idx: Target class index (if None, uses predicted class)
            
        Returns:
            Grad-CAM heatmap as numpy array
        """
        # Forward pass
        output = self.model(input_tensor)
        
        if class_idx is None:
            class_idx = output.argmax(dim=1).item()
        
        # Zero gradients
        self.model.zero_grad()
        
        # Backward pass for target class
        class_score = output[0, class_idx]
        class_score.backward()
        
        # Get gradients and activations
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
        cam = cam.detach().cpu().numpy()
        
        return cam
    
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

def get_grad_cam_for_model(model_type: str, model: nn.Module, 
                          input_tensor: torch.Tensor, original_image: np.ndarray,
                          class_idx: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate Grad-CAM visualization for specific model type
    
    Args:
        model_type: Type of model ('chest_xray' or 'brain_mri')
        model: PyTorch model
        input_tensor: Preprocessed input tensor
        original_image: Original image as numpy array
        class_idx: Target class index
        
    Returns:
        Tuple of (heatmap, overlay_image)
    """
    # Determine target layer based on model type
    if model_type == 'chest_xray':
        target_layer = 'layer4'  # Last residual block in ResNet
    elif model_type == 'brain_mri':
        target_layer = 'features.8'  # Last feature layer in EfficientNet
    else:
        target_layer = 'layer4'  # Default for ResNet-like models
    
    # Create Grad-CAM instance
    grad_cam = GradCAM(model, target_layer)
    
    # Generate CAM
    try:
        cam = grad_cam.generate_cam(input_tensor, class_idx)
        
        # Create overlay
        overlay = grad_cam.overlay_heatmap(original_image, cam)
        
        return cam, overlay
        
    except Exception as e:
        logger.error(f"Error generating Grad-CAM: {e}")
        # Return empty arrays if Grad-CAM fails
        h, w = original_image.shape[:2]
        return np.zeros((h, w)), original_image.copy()
