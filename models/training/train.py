import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
from datetime import datetime
import json
from dataset import MedicalImageDataset
from data_augmentation import get_train_transforms, get_val_transforms

class MedicalImageTrainer:
    """Trainer class for medical image classification"""
    
    def __init__(self, model_type="chest_xray", data_dir="./data", batch_size=32, learning_rate=0.001):
        """
        Initialize trainer
        
        Args:
            model_type: Type of model ('chest_xray' or 'brain_mri')
            data_dir: Directory containing dataset
            batch_size: Batch size for training
            learning_rate: Learning rate for optimizer
        """
        self.model_type = model_type
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Create model
        self.model = self._create_model()
        self.model.to(self.device)
        
        # Setup optimizer and loss function
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate, weight_decay=1e-4)
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(self.optimizer, mode='min', patience=3, factor=0.1)
        
        # Training history
        self.train_losses = []
        self.val_losses = []
        self.train_accuracies = []
        self.val_accuracies = []
        
        print(f"Initialized {model_type} trainer on {self.device}")
    
    def _create_model(self):
        """Create model based on type"""
        if self.model_type == "chest_xray":
            # ResNet50 for chest X-ray classification
            model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
            num_features = model.fc.in_features
            model.fc = nn.Sequential(
                nn.Dropout(0.5),
                nn.Linear(num_features, 2)  # Normal, Pneumonia
            )
        elif self.model_type == "brain_mri":
            # EfficientNet-B0 for brain MRI classification
            model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
            num_features = model.classifier[1].in_features
            model.classifier[1] = nn.Sequential(
                nn.Dropout(0.5),
                nn.Linear(num_features, 4)  # glioma, meningioma, notumor, pituitary
            )
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
        
        return model
    
    def _prepare_data(self):
        """Prepare data loaders"""
        # Prepare data directories
        train_dir = os.path.join(self.data_dir, "train")
        val_dir = os.path.join(self.data_dir, "val")
        test_dir = os.path.join(self.data_dir, "test")
        
        # Create datasets
        train_dataset = MedicalImageDataset(
            train_dir, 
            transform=get_train_transforms(self.model_type)
        )
        val_dataset = MedicalImageDataset(
            val_dir, 
            transform=get_val_transforms(self.model_type)
        )
        test_dataset = MedicalImageDataset(
            test_dir, 
            transform=get_val_transforms(self.model_type)
        )
        
        # Create data loaders
        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True, num_workers=4)
        val_loader = DataLoader(val_dataset, batch_size=self.batch_size, shuffle=False, num_workers=4)
        test_loader = DataLoader(test_dataset, batch_size=self.batch_size, shuffle=False, num_workers=4)
        
        return train_loader, val_loader, test_loader
    
    def train_epoch(self, train_loader):
        """Train for one epoch"""
        self.model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        for batch_idx, (images, labels) in enumerate(train_loader):
            images, labels = images.to(self.device), labels.to(self.device)
            
            # Zero gradients
            self.optimizer.zero_grad()
            
            # Forward pass
            outputs = self.model(images)
            loss = self.criterion(outputs, labels)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            # Statistics
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
            if batch_idx % 100 == 0:
                print(f'Batch {batch_idx}, Loss: {loss.item():.4f}')
        
        epoch_loss = running_loss / len(train_loader)
        epoch_acc = 100 * correct / total
        
        return epoch_loss, epoch_acc
    
    def validate_epoch(self, val_loader):
        """Validate for one epoch"""
        self.model.eval()
        running_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(self.device), labels.to(self.device)
                
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)
                
                running_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        epoch_loss = running_loss / len(val_loader)
        epoch_acc = 100 * correct / total
        
        return epoch_loss, epoch_acc
    
    def train(self, num_epochs=50):
        """Train the model"""
        print(f"Starting training for {num_epochs} epochs...")
        
        # Prepare data
        train_loader, val_loader, test_loader = self._prepare_data()
        
        best_val_acc = 0.0
        best_model_path = f"../models/inference/{self.model_type}_best_model.pth"
        
        for epoch in range(num_epochs):
            print(f'\nEpoch {epoch + 1}/{num_epochs}')
            print('-' * 50)
            
            # Train
            train_loss, train_acc = self.train_epoch(train_loader)
            
            # Validate
            val_loss, val_acc = self.validate_epoch(val_loader)
            
            # Update learning rate
            self.scheduler.step(val_loss)
            
            # Save history
            self.train_losses.append(train_loss)
            self.val_losses.append(val_loss)
            self.train_accuracies.append(train_acc)
            self.val_accuracies.append(val_acc)
            
            print(f'Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%')
            print(f'Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%')
            
            # Save best model
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                torch.save({
                    'epoch': epoch + 1,
                    'model_state_dict': self.model.state_dict(),
                    'optimizer_state_dict': self.optimizer.state_dict(),
                    'val_acc': val_acc,
                    'val_loss': val_loss,
                    'model_type': self.model_type
                }, best_model_path)
                print(f'New best model saved with validation accuracy: {val_acc:.2f}%')
        
        print(f'\nTraining completed! Best validation accuracy: {best_val_acc:.2f}%')
        
        # Final evaluation on test set
        test_acc, test_report = self.evaluate(test_loader)
        print(f'Test Accuracy: {test_acc:.2f}%')
        print('\nClassification Report:')
        print(test_report)
        
        # Save training history
        self.save_training_history()
        
        # Plot training curves
        self.plot_training_curves()
        
        return best_model_path
    
    def evaluate(self, test_loader):
        """Evaluate model on test set"""
        self.model.eval()
        all_predictions = []
        all_labels = []
        correct = 0
        total = 0
        
        with torch.no_grad():
            for images, labels in test_loader:
                images, labels = images.to(self.device), labels.to(self.device)
                outputs = self.model(images)
                _, predicted = torch.max(outputs.data, 1)
                
                all_predictions.extend(predicted.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
                
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        accuracy = 100 * correct / total
        
        # Generate classification report
        if self.model_type == 'chest_xray':
            class_names = ['Normal', 'Pneumonia']
        elif self.model_type == 'brain_mri':
            class_names = ['glioma', 'meningioma', 'notumor', 'pituitary']
        else:
            class_names = ['Unknown']
        report = classification_report(all_labels, all_predictions, target_names=class_names)
        
        return accuracy, report
    
    def save_training_history(self):
        """Save training history to JSON file"""
        history = {
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'train_accuracies': self.train_accuracies,
            'val_accuracies': self.val_accuracies,
            'model_type': self.model_type,
            'timestamp': datetime.now().isoformat()
        }
        
        history_path = f"../models/inference/{self.model_type}_training_history.json"
        os.makedirs(os.path.dirname(history_path), exist_ok=True)
        
        with open(history_path, 'w') as f:
            json.dump(history, f, indent=2)
        
        print(f"Training history saved to {history_path}")
    
    def plot_training_curves(self):
        """Plot training curves"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # Loss curves
        ax1.plot(self.train_losses, label='Train Loss')
        ax1.plot(self.val_losses, label='Validation Loss')
        ax1.set_title('Training and Validation Loss')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Loss')
        ax1.legend()
        ax1.grid(True)
        
        # Accuracy curves
        ax2.plot(self.train_accuracies, label='Train Accuracy')
        ax2.plot(self.val_accuracies, label='Validation Accuracy')
        ax2.set_title('Training and Validation Accuracy')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Accuracy (%)')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        
        # Save plot
        plot_path = f"../models/inference/{self.model_type}_training_curves.png"
        os.makedirs(os.path.dirname(plot_path), exist_ok=True)
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"Training curves saved to {plot_path}")

def main():
    """Main training function"""
    # Configuration
    config = {
        'brain_mri': {
            'data_dir': '../../data/brain_mri',
            'batch_size': 16,
            'learning_rate': 0.0001,
            'num_epochs': 10  # Reduced for faster training
        }
    }
    
    # Train models
    for model_type, params in config.items():
        print(f"\n{'='*60}")
        print(f"Training {model_type.upper()} Model")
        print(f"{'='*60}")
        
        trainer = MedicalImageTrainer(
            model_type=model_type,
            data_dir=params['data_dir'],
            batch_size=params['batch_size'],
            learning_rate=params['learning_rate']
        )
        
        best_model_path = trainer.train(num_epochs=params['num_epochs'])
        print(f"Best model saved to: {best_model_path}")

if __name__ == "__main__":
    main()
