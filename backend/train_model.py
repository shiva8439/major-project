import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
import os
from PIL import Image
import numpy as np
from pathlib import Path

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
            if os.path.isdir(class_dir):
                for img_name in os.listdir(class_dir):
                    if img_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                        self.file_list.append((os.path.join(class_dir, img_name), class_idx))
    
    def __len__(self):
        return len(self.file_list)
    
    def __getitem__(self, idx):
        img_path, label = self.file_list[idx]
        try:
            image = Image.open(img_path).convert('RGB')
            if self.transform:
                image = self.transform(image)
            return image, label
        except Exception as e:
            print(f"Error loading image {img_path}: {e}")
            # Return a dummy image
            dummy_image = torch.zeros(3, 224, 224)
            return dummy_image, label

# Training function
def train_model():
    print("🧠 Starting Brain Tumor Model Training...")
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create demo dataset if real dataset doesn't exist
    train_dir = Path("dataset/train")
    if not train_dir.exists():
        print("⚠️ Dataset not found. Creating demo dataset for training...")
        train_dir.mkdir(parents=True, exist_ok=True)
        val_dir = Path("dataset/val")
        val_dir.mkdir(parents=True, exist_ok=True)
        
        # Create demo class folders
        classes = ['no_tumor', 'glioma', 'meningioma', 'pituitary', 'metastasis']
        for class_name in classes:
            (train_dir / class_name).mkdir(exist_ok=True)
            (val_dir / class_name).mkdir(exist_ok=True)
            
            # Create dummy images for demo
            for i in range(10):  # 10 images per class
                dummy_img = Image.new('RGB', (224, 224), color=(i*50, 100, 100))
                dummy_img.save(train_dir / class_name / f"dummy_{i}.jpg")
                dummy_img.save(val_dir / class_name / f"dummy_{i}.jpg")
    
    # Load datasets
    train_dataset = BrainMRIDataset(str(train_dir), transform=transform)
    val_dataset = BrainMRIDataset(str(train_dir.parent / "val"), transform=transform)
    
    print(f"Training samples: {len(train_dataset)}")
    print(f"Validation samples: {len(val_dataset)}")
    
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)
    
    # Model
    model = models.resnet18(weights='IMAGENET1K_V1')
    model.fc = nn.Linear(model.fc.in_features, 5)  # 5 classes
    model = model.to(device)
    
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    # Training loop
    num_epochs = 10  # Reduced for demo
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        
        for batch_idx, (images, labels) in enumerate(train_loader):
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            
            if batch_idx % 10 == 0:
                print(f'Epoch [{epoch+1}/{num_epochs}], Batch [{batch_idx+1}/{len(train_loader)}], Loss: {loss.item():.4f}')
        
        # Validation
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        val_accuracy = 100 * correct / total
        print(f'Validation Accuracy: {val_accuracy:.2f}%')
    
    # Save model
    model_path = Path("app/models/brain_mri_model.pth")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({
        'model_state_dict': model.state_dict(),
        'classes': ['no_tumor', 'glioma', 'meningioma', 'pituitary', 'metastasis'],
        'num_epochs': num_epochs,
        'val_accuracy': val_accuracy
    }, model_path)
    
    print(f"✅ Model saved to {model_path}")
    print(f"🎯 Training completed! Validation accuracy: {val_accuracy:.2f}%")

if __name__ == "__main__":
    train_model()
