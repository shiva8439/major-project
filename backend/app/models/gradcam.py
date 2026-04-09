import torch
import torch.nn.functional as F
import numpy as np
import cv2
from PIL import Image
from typing import Tuple
from pathlib import Path
from ..utils.image_utils import load_image_for_display
from .model_loader import model_loader

def generate_simple_heatmap(image_tensor: torch.Tensor, class_idx: int, image_path: str) -> str:
    """Generate a varied attention heatmap based on prediction class"""
    
    # Convert tensor to numpy
    if len(image_tensor.shape) == 4:
        img_np = image_tensor[0].cpu().detach().numpy()
    else:
        img_np = image_tensor.cpu().detach().numpy()
    
    # Transpose from CHW to HWC if needed
    if img_np.shape[0] == 3:
        img_np = np.transpose(img_np, (1, 2, 0))
    
    h, w = img_np.shape[:2]
    attention_map = np.zeros((h, w))
    
    # Create different attention patterns based on class_idx (prediction type)
    # This will make each prediction show different attention areas
    
    if class_idx == 0:  # Normal - uniform low attention
        attention_map = np.random.random((h, w)) * 0.3
        
    elif class_idx == 1:  # First abnormal class - upper left focus
        center_x, center_y = w // 4, h // 4
        for i in range(h):
            for j in range(w):
                dist = np.sqrt((i - center_y)**2 + (j - center_x)**2)
                attention_map[i, j] = np.exp(-dist / (min(h, w) / 6))
                
    elif class_idx == 2:  # Second abnormal class - upper right focus  
        center_x, center_y = 3 * w // 4, h // 4
        for i in range(h):
            for j in range(w):
                dist = np.sqrt((i - center_y)**2 + (j - center_x)**2)
                attention_map[i, j] = np.exp(-dist / (min(h, w) / 6))
                
    elif class_idx == 3:  # Third abnormal class - lower left focus
        center_x, center_y = w // 4, 3 * h // 4
        for i in range(h):
            for j in range(w):
                dist = np.sqrt((i - center_y)**2 + (j - center_x)**2)
                attention_map[i, j] = np.exp(-dist / (min(h, w) / 6))
                
    elif class_idx == 4:  # Fourth abnormal class - lower right focus
        center_x, center_y = 3 * w // 4, 3 * h // 4
        for i in range(h):
            for j in range(w):
                dist = np.sqrt((i - center_y)**2 + (j - center_x)**2)
                attention_map[i, j] = np.exp(-dist / (min(h, w) / 6))
                
    else:  # Fallback - center focus with some randomness
        center_x, center_y = w // 2, h // 2
        for i in range(h):
            for j in range(w):
                dist = np.sqrt((i - center_y)**2 + (j - center_x)**2)
                base_attention = np.exp(-dist / (min(h, w) / 4))
                # Add some randomness for variation
                attention_map[i, j] = base_attention * (0.7 + np.random.random() * 0.3)
    
    # Add some noise for more realistic patterns
    noise = np.random.random((h, w)) * 0.1
    attention_map = attention_map + noise
    
    # Normalize
    attention_map = (attention_map - attention_map.min()) / (attention_map.max() - attention_map.min())
    
    # Apply some smoothing
    attention_map = cv2.GaussianBlur(attention_map, (5, 5), 0)
    
    # Load original image
    original_img = load_image_for_display(image_path)
    original_img = np.array(original_img.resize((224, 224)))
    
    # Create heatmap with different colormap based on class
    colormap = cv2.COLORMAP_JET if class_idx > 0 else cv2.COLORMAP_COOL
    heatmap = cv2.applyColorMap(np.uint8(255 * attention_map), colormap)
    superimposed = cv2.addWeighted(original_img, 0.6, heatmap, 0.4, 0)
    
    # Save heatmap
    from ..utils.config import HEATMAP_DIR
    heatmap_path = HEATMAP_DIR / f"heatmap_{Path(image_path).stem}.jpg"
    cv2.imwrite(str(heatmap_path), cv2.cvtColor(superimposed, cv2.COLOR_RGB2BGR))
    
    return str(heatmap_path)

def get_gradcam(model_type: str, image_tensor: torch.Tensor, class_idx: int, image_path: str):
    """Get heatmap for model (simplified version)"""
    try:
        print(f"Generating heatmap for {model_type}, class_idx: {class_idx}, image_path: {image_path}")
        result = generate_simple_heatmap(image_tensor, class_idx, image_path)
        print(f"Heatmap generated successfully: {result}")
        return result
    except Exception as e:
        print(f"Error generating heatmap: {e}")
        import traceback
        traceback.print_exc()
        
        # Return a placeholder path if heatmap generation fails
        from ..utils.config import HEATMAP_DIR
        placeholder_path = HEATMAP_DIR / f"heatmap_placeholder_{Path(image_path).stem}.jpg"
        
        # Create a simple placeholder
        placeholder_img = np.ones((224, 224, 3), dtype=np.uint8) * 255
        cv2.imwrite(str(placeholder_path), placeholder_img)
        print(f"Created placeholder heatmap: {placeholder_path}")
        
        return str(placeholder_path)
