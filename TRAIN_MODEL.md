# 🧠 Train Brain Tumor Detection Model

## 📋 Requirements for Training

### 1. Dataset Collection
- **Brain MRI Images**: Collect 1000+ images per class
- **Classes**: No Tumor, Glioma, Meningioma, Pituitary Tumor, Metastasis
- **Image Format**: JPG/PNG, 224x224 pixels
- **Quality**: High-quality medical MRI scans

### 2. Dataset Structure
```
dataset/
├── train/
│   ├── no_tumor/
│   ├── glioma/
│   ├── meningioma/
│   ├── pituitary/
│   └── metastasis/
├── val/
│   ├── no_tumor/
│   ├── glioma/
│   ├── meningioma/
│   ├── pituitary/
│   └── metastasis/
└── test/
    ├── no_tumor/
    ├── glioma/
    ├── meningioma/
    ├── pituitary/
    └── metastasis/
```

### 3. Training Script
Create `train_model.py`:

```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
import os
from PIL import Image
import numpy as np

# Data preparation
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Custom dataset class
class BrainMRIDataset(torch.utils.data.Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.classes = sorted(os.listdir(root_dir))
        self.file_list = []
        
        for class_idx, class_name in enumerate(self.classes):
            class_dir = os.path.join(root_dir, class_name)
            for img_name in os.listdir(class_dir):
                self.file_list.append((os.path.join(class_dir, img_name), class_idx))
    
    def __len__(self):
        return len(self.file_list)
    
    def __getitem__(self, idx):
        img_path, label = self.file_list[idx]
        image = Image.open(img_path).convert('RGB')
        if self.transform:
            image = self.transform(image)
        return image, label

# Training function
def train_model():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Load datasets
    train_dataset = BrainMRIDataset('dataset/train', transform=transform)
    val_dataset = BrainMRIDataset('dataset/val', transform=transform)
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
    
    # Model
    model = models.resnet18(pretrained=True)
    model.fc = nn.Linear(model.fc.in_features, 5)  # 5 classes
    model = model.to(device)
    
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    # Training loop
    for epoch in range(50):  # 50 epochs
        model.train()
        for batch_idx, (images, labels) in enumerate(train_loader):
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            if batch_idx % 100 == 0:
                print(f'Epoch [{epoch+1}/50], Batch [{batch_idx+1}/{len(train_loader)}], Loss: {loss.item():.4f}')
    
    # Save model
    torch.save(model.state_dict(), 'brain_mri_model.pth')
    print("Model saved successfully!")

if __name__ == "__main__":
    train_model()
```

### 4. Training Commands

#### Install Requirements:
```bash
pip install torch torchvision pillow numpy
```

#### Start Training:
```bash
cd backend
python train_model.py
```

### 5. Model Evaluation
After training, test the model:
```python
python -c "
from app.models.model_loader import model_loader
from torchvision import transforms
from PIL import Image
import torch

# Test with sample image
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

image = Image.open('test_image.jpg').convert('RGB')
image_tensor = transform(image).unsqueeze(0)

model = model_loader.load_model(Path('app/models/brain_mri_model.pth'), 'brain_mri')
prediction, confidence = model_loader.predict('brain_mri', image_tensor)

print(f'Prediction: {prediction}')
print(f'Confidence: {confidence:.2%}')
"
```

## 🎯 Training Tips

### Data Quality:
- Use diverse, high-quality MRI scans
- Balance classes (200+ images per class)
- Augment data: rotations, flips, brightness changes

### Training Parameters:
- **Epochs**: 50-100 for good convergence
- **Batch Size**: 16-32 (based on GPU memory)
- **Learning Rate**: 0.001-0.0001
- **Validation**: Check every epoch

### Expected Results:
- **Training Time**: 2-4 hours on GPU
- **Accuracy**: 85-95% on test set
- **Model Size**: ~50MB

## 🚀 Next Steps

1. **Collect Dataset**: Gather brain MRI images
2. **Prepare Data**: Organize into class folders
3. **Run Training**: Execute training script
4. **Evaluate Model**: Test accuracy and confidence
5. **Deploy Model**: Replace demo model with trained model

**After training, your app will use real AI model predictions!** 🧠✨
