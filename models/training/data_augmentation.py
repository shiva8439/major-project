import torchvision.transforms as transforms
from PIL import Image, ImageEnhance, ImageFilter
import random
import numpy as np

class MedicalImageAugmentation:
    """Custom augmentation for medical images"""
    
    def __init__(self, probability=0.5):
        self.probability = probability
    
    def __call__(self, image):
        """Apply random augmentations to the image"""
        if random.random() < self.probability:
            # Random brightness adjustment
            if random.random() < 0.5:
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(random.uniform(0.8, 1.2))
            
            # Random contrast adjustment
            if random.random() < 0.5:
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(random.uniform(0.8, 1.2))
            
            # Random Gaussian blur (subtle)
            if random.random() < 0.3:
                image = image.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.1, 0.5)))
        
        return image

def get_train_transforms(model_type: str = "chest_xray"):
    """
    Get training transforms with data augmentation
    
    Args:
        model_type: Type of model (chest_xray or brain_mri)
        
    Returns:
        Composed transforms for training
    """
    # Base transforms
    base_transforms = [
        transforms.Resize((256, 256)),  # Resize to larger size first
        transforms.RandomCrop((224, 224)),  # Random crop
        transforms.RandomHorizontalFlip(p=0.5),  # Horizontal flip (safe for medical images)
        MedicalImageAugmentation(probability=0.7),  # Custom medical augmentations
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],  # ImageNet normalization
            std=[0.229, 0.224, 0.225]
        )
    ]
    
    # Add model-specific augmentations
    if model_type == "chest_xray":
        # Chest X-ray specific augmentations
        chest_specific = [
            transforms.RandomRotation(degrees=5),  # Small rotation
            transforms.RandomAffine(degrees=0, translate=(0.05, 0.05)),  # Small translation
        ]
        base_transforms.insert(2, transforms.RandomChoice(chest_specific))
    
    elif model_type == "brain_mri":
        # Brain MRI specific augmentations
        mri_specific = [
            transforms.RandomRotation(degrees=3),  # Very small rotation for MRI
            transforms.RandomAffine(degrees=0, translate=(0.02, 0.02)),  # Very small translation
        ]
        base_transforms.insert(2, transforms.RandomChoice(mri_specific))
    
    return transforms.Compose(base_transforms)

def get_val_transforms(model_type: str = "chest_xray"):
    """
    Get validation/test transforms (no augmentation)
    
    Args:
        model_type: Type of model (chest_xray or brain_mri)
        
    Returns:
        Composed transforms for validation
    """
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

def get_inference_transforms():
    """
    Get transforms for inference
    
    Returns:
        Composed transforms for inference
    """
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

class MedicalImageTransforms:
    """Advanced transforms specifically for medical images"""
    
    @staticmethod
    def histogram_equalization(image):
        """Apply histogram equalization to enhance contrast"""
        if image.mode != 'L':
            image = image.convert('L')
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Apply histogram equalization
        from skimage import exposure
        img_equalized = exposure.equalize_hist(img_array)
        
        # Convert back to PIL Image
        return Image.fromarray((img_equalized * 255).astype(np.uint8))
    
    @staticmethod
    def clahe_transform(image):
        """Apply Contrast Limited Adaptive Histogram Equalization"""
        if image.mode != 'L':
            image = image.convert('L')
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Apply CLAHE
        from skimage import exposure
        img_clahe = exposure.equalize_adapthist(img_array, clip_limit=0.03)
        
        # Convert back to PIL Image
        return Image.fromarray((img_clahe * 255).astype(np.uint8))
    
    @staticmethod
    def noise_injection(image, noise_factor=0.05):
        """Inject random noise into the image"""
        img_array = np.array(image)
        
        # Add Gaussian noise
        noise = np.random.normal(0, noise_factor * 255, img_array.shape)
        img_noisy = img_array + noise
        
        # Clip values to valid range
        img_noisy = np.clip(img_noisy, 0, 255)
        
        return Image.fromarray(img_noisy.astype(np.uint8))
    
    @staticmethod
    def elastic_transform(image, alpha=1000, sigma=8):
        """Apply elastic transformation for data augmentation"""
        from scipy.ndimage import gaussian_filter, map_coordinates
        
        img_array = np.array(image)
        shape = img_array.shape
        
        # Generate random displacement fields
        dx = gaussian_filter((np.random.rand(*shape) * 2 - 1), sigma, mode="constant", cval=0) * alpha
        dy = gaussian_filter((np.random.rand(*shape) * 2 - 1), sigma, mode="constant", cval=0) * alpha
        
        # Create coordinate grids
        x, y = np.meshgrid(np.arange(shape[1]), np.arange(shape[0]))
        indices = np.reshape(y + dy, (-1, 1)), np.reshape(x + dx, (-1, 1))
        
        # Apply transformation
        distorted_image = np.zeros_like(img_array)
        for i in range(shape[2]):
            distorted_image[:, :, i] = map_coordinates(img_array[:, :, i], indices, order=1, mode='reflect').reshape(shape[:2])
        
        return Image.fromarray(distorted_image.astype(np.uint8))

# Example usage and testing
if __name__ == "__main__":
    from PIL import Image
    import matplotlib.pyplot as plt
    
    # Create a sample image
    sample_img = Image.new('RGB', (224, 224), color='gray')
    
    # Test transforms
    train_transform = get_train_transforms("chest_xray")
    val_transform = get_val_transforms("chest_xray")
    
    # Apply transforms
    train_img = train_transform(sample_img)
    val_img = val_transform(sample_img)
    
    print("Transform shapes:")
    print(f"Train: {train_img.shape}")
    print(f"Val: {val_img.shape}")
    
    # Test advanced transforms
    advanced = MedicalImageTransforms()
    
    # Convert to grayscale for some transforms
    gray_img = sample_img.convert('L')
    
    # Apply histogram equalization
    hist_eq_img = advanced.histogram_equalization(gray_img)
    
    # Apply CLAHE
    clahe_img = advanced.clahe_transform(gray_img)
    
    # Apply noise injection
    noise_img = advanced.noise_injection(sample_img)
    
    print("Advanced transforms applied successfully!")
