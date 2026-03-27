import torch
from torch.utils.data import Dataset
from PIL import Image
import os
import numpy as np
from typing import List, Tuple, Optional

class MedicalImageDataset(Dataset):
    """Custom dataset for medical images"""
    
    def __init__(self, root_dir: str, transform=None):
        """
        Initialize dataset
        
        Args:
            root_dir: Directory containing class folders
            transform: Optional transform to be applied
        """
        self.root_dir = root_dir
        self.transform = transform
        self.images = []
        self.labels = []
        self.class_names = []
        
        # Load image paths and labels
        self._load_data()
    
    def _load_data(self):
        """Load image paths and labels from directory structure"""
        if not os.path.exists(self.root_dir):
            raise FileNotFoundError(f"Directory not found: {self.root_dir}")
        
        # Get class names (folder names)
        self.class_names = sorted([d for d in os.listdir(self.root_dir) 
                                  if os.path.isdir(os.path.join(self.root_dir, d))])
        
        print(f"Found classes: {self.class_names}")
        
        # Load images for each class
        for class_idx, class_name in enumerate(self.class_names):
            class_dir = os.path.join(self.root_dir, class_name)
            
            # Get all image files in the class directory
            image_files = []
            try:
                all_files = os.listdir(class_dir)
                print(f"Found {len(all_files)} files in {class_dir}")
                for ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
                    matching_files = [f for f in all_files if f.lower().endswith(ext.lower())]
                    image_files.extend(matching_files)
                    print(f"Found {len(matching_files)} {ext} files")
            except Exception as e:
                print(f"Error listing files in {class_dir}: {e}")
            
            # Add image paths and labels
            for img_file in image_files:
                img_path = os.path.join(class_dir, img_file)
                self.images.append(img_path)
                self.labels.append(class_idx)
        
        print(f"Loaded {len(self.images)} images from {len(self.class_names)} classes")
    
    def __len__(self) -> int:
        """Return the total number of samples"""
        return len(self.images)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        """
        Get a sample from the dataset
        
        Args:
            idx: Index of the sample
            
        Returns:
            Tuple of (image_tensor, label)
        """
        # Load image
        img_path = self.images[idx]
        label = self.labels[idx]
        
        try:
            # Open image
            image = Image.open(img_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Apply transforms if provided
            if self.transform:
                image = self.transform(image)
            
            return image, label
            
        except Exception as e:
            print(f"Error loading image {img_path}: {e}")
            # Return a default black image if loading fails
            default_image = Image.new('RGB', (224, 224), color='black')
            if self.transform:
                default_image = self.transform(default_image)
            return default_image, label
    
    def get_class_name(self, label: int) -> str:
        """Get class name from label index"""
        if 0 <= label < len(self.class_names):
            return self.class_names[label]
        return "Unknown"
    
    def get_class_distribution(self) -> dict:
        """Get distribution of samples across classes"""
        distribution = {}
        for class_name in self.class_names:
            distribution[class_name] = 0
        
        for label in self.labels:
            class_name = self.get_class_name(label)
            distribution[class_name] += 1
        
        return distribution

def create_sample_dataset(output_dir: str, dataset_type: str = "chest_xray"):
    """
    Create a sample dataset structure for testing
    
    Args:
        output_dir: Directory to create sample dataset
        dataset_type: Type of dataset (chest_xray or brain_mri)
    """
    import random
    from PIL import Image, ImageDraw
    
    # Create directory structure
    if dataset_type == "chest_xray":
        classes = ["Normal", "Pneumonia"]
    else:  # brain_mri
        classes = ["Normal", "Tumor"]
    
    for split in ["train", "val", "test"]:
        split_dir = os.path.join(output_dir, dataset_type, split)
        os.makedirs(split_dir, exist_ok=True)
        
        for class_name in classes:
            class_dir = os.path.join(split_dir, class_name)
            os.makedirs(class_dir, exist_ok=True)
            
            # Create sample images
            num_samples = {"train": 50, "val": 20, "test": 20}[split]
            
            for i in range(num_samples):
                # Create a random image
                img = Image.new('RGB', (224, 224), color='white')
                draw = ImageDraw.Draw(img)
                
                # Add some random patterns to simulate medical images
                for _ in range(random.randint(5, 15)):
                    x1, y1 = random.randint(0, 200), random.randint(0, 200)
                    x2, y2 = x1 + random.randint(10, 50), y1 + random.randint(10, 50)
                    color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
                    draw.rectangle([x1, y1, x2, y2], fill=color, outline='black')
                
                # Save image
                img_path = os.path.join(class_dir, f"sample_{i:03d}.png")
                img.save(img_path)
    
    print(f"Sample dataset created at {output_dir}")

if __name__ == "__main__":
    # Example usage
    create_sample_dataset("../data", "chest_xray")
    create_sample_dataset("../data", "brain_mri")
