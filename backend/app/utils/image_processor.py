import cv2
import numpy as np
from PIL import Image
import torch
import torchvision.transforms as transforms
from typing import Tuple, Optional
import io
import base64

def is_grayscale(image):
    """Check if image is mostly grayscale"""
    if len(image.shape) == 3:
        r, g, b = image[:,:,0], image[:,:,1], image[:,:,2]
        return np.allclose(r, g, atol=10) and np.allclose(g, b, atol=10)
    return True

def edge_density(image):
    """Check edge density for medical images"""
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    return edges.mean()

def is_medical_image(image, image_type):
    """
    Validate if image is a proper medical scan
    
    Args:
        image: Image as numpy array
        image_type: Type of medical image (chest_xray, brain_mri)
        
    Returns:
        bool: True if valid medical image, False otherwise
    """
    # Step 1: grayscale check
    if not is_grayscale(image):
        return False
    
    # Step 2: edge density check
    edges = edge_density(image)
    if edges < 5:
        return False
    
    return True

class ImageProcessor:
    """Handles image preprocessing for medical image analysis"""
    
    def __init__(self):
        # Define image transformations
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    
    def preprocess_image(self, image_data: bytes) -> Tuple[torch.Tensor, np.ndarray]:
        """
        Preprocess uploaded image for model inference
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Tuple of (processed_tensor, original_image_array)
        """
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
    
    def resize_for_display(self, image: np.ndarray, max_size: int = 512) -> np.ndarray:
        """
        Resize image for display while maintaining aspect ratio
        
        Args:
            image: Input image as numpy array
            max_size: Maximum dimension size
            
        Returns:
            Resized image
        """
        height, width = image.shape[:2]
        
        if max(height, width) <= max_size:
            return image
        
        if height > width:
            new_height = max_size
            new_width = int(width * (max_size / height))
        else:
            new_width = max_size
            new_height = int(height * (max_size / width))
        
        return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    def image_to_base64(self, image: np.ndarray, format: str = 'PNG') -> str:
        """
        Convert numpy array to base64 string
        
        Args:
            image: Image as numpy array
            format: Image format (PNG, JPEG, etc.)
            
        Returns:
            Base64 encoded image string
        """
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
    
    def validate_image(self, image_data: bytes) -> bool:
        """
        Validate if the uploaded file is a valid image
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            True if valid image, False otherwise
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            image.verify()  # Verify that it's a valid image
            return True
        except Exception:
            return False
    
    def get_image_info(self, image_data: bytes) -> dict:
        """
        Get basic information about the uploaded image
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dictionary with image information
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            return {
                'format': image.format,
                'mode': image.mode,
                'size': image.size,
                'file_size': len(image_data)
            }
        except Exception:
            return {}
