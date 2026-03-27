import torch
import torch.nn as nn
import torchvision.models as models
from typing import Dict, Any

class MedicalImageClassifier(nn.Module):
    """Base class for medical image classification models"""
    
    def __init__(self, num_classes: int = 2, pretrained: bool = True):
        """
        Initialize base classifier
        
        Args:
            num_classes: Number of output classes
            pretrained: Whether to use pretrained weights
        """
        super(MedicalImageClassifier, self).__init__()
        self.num_classes = num_classes
        self.pretrained = pretrained
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        
        return {
            'model_type': self.__class__.__name__,
            'total_parameters': total_params,
            'trainable_parameters': trainable_params,
            'num_classes': self.num_classes,
            'pretrained': self.pretrained
        }

class ChestXRayClassifier(MedicalImageClassifier):
    """ResNet50-based classifier for chest X-ray images"""
    
    def __init__(self, num_classes: int = 2, pretrained: bool = True):
        super(ChestXRayClassifier, self).__init__(num_classes, pretrained)
        
        # Load ResNet50
        if pretrained:
            self.backbone = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
        else:
            self.backbone = models.resnet50(weights=None)
        
        # Freeze early layers (optional)
        for param in list(self.backbone.parameters())[:-10]:  # Freeze all except last 10 layers
            param.requires_grad = False
        
        # Modify final layer for binary classification
        num_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(512, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(128, num_classes)
        )
    
    def forward(self, x):
        return self.backbone(x)
    
    def get_feature_maps(self, x):
        """Extract feature maps from intermediate layers"""
        feature_maps = {}
        
        # Hook function to capture feature maps
        def hook_fn(module, input, output, name):
            feature_maps[name] = output
        
        # Register hooks
        hooks = []
        hook_layers = {
            'layer1': self.backbone.layer1,
            'layer2': self.backbone.layer2,
            'layer3': self.backbone.layer3,
            'layer4': self.backbone.layer4
        }
        
        for name, layer in hook_layers.items():
            hook = layer.register_forward_hook(lambda module, input, output, name=name: hook_fn(module, input, output, name))
            hooks.append(hook)
        
        # Forward pass
        with torch.no_grad():
            output = self.backbone(x)
        
        # Remove hooks
        for hook in hooks:
            hook.remove()
        
        return feature_maps, output

class BrainMRIClassifier(MedicalImageClassifier):
    """EfficientNet-B0 based classifier for brain MRI images"""
    
    def __init__(self, num_classes: int = 2, pretrained: bool = True):
        super(BrainMRIClassifier, self).__init__(num_classes, pretrained)
        
        # Load EfficientNet-B0
        if pretrained:
            self.backbone = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
        else:
            self.backbone = models.efficientnet_b0(weights=None)
        
        # Freeze early layers
        for param in list(self.backbone.parameters())[:-5]:  # Freeze all except last 5 layers
            param.requires_grad = False
        
        # Modify final layer for binary classification
        num_features = self.backbone.classifier[1].in_features
        self.backbone.classifier[1] = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(256, 64),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(64, num_classes)
        )
    
    def forward(self, x):
        return self.backbone(x)
    
    def get_feature_maps(self, x):
        """Extract feature maps from intermediate layers"""
        feature_maps = {}
        
        # Hook function to capture feature maps
        def hook_fn(module, input, output, name):
            feature_maps[name] = output
        
        # Register hooks
        hooks = []
        hook_layers = {
            'features.3': self.backbone.features[3],
            'features.5': self.backbone.features[5],
            'features.7': self.backbone.features[7],
            'features.8': self.backbone.features[8]
        }
        
        for name, layer in hook_layers.items():
            hook = layer.register_forward_hook(lambda module, input, output, name=name: hook_fn(module, input, output, name))
            hooks.append(hook)
        
        # Forward pass
        with torch.no_grad():
            output = self.backbone(x)
        
        # Remove hooks
        for hook in hooks:
            hook.remove()
        
        return feature_maps, output

class EnsembleClassifier(nn.Module):
    """Ensemble of multiple models for better performance"""
    
    def __init__(self, models: list):
        """
        Initialize ensemble classifier
        
        Args:
            models: List of models to ensemble
        """
        super(EnsembleClassifier, self).__init__()
        self.models = nn.ModuleList(models)
        self.num_models = len(models)
    
    def forward(self, x):
        """Forward pass through all models and average predictions"""
        outputs = []
        
        for model in self.models:
            output = model(x)
            outputs.append(output)
        
        # Average the predictions
        avg_output = torch.stack(outputs).mean(dim=0)
        return avg_output
    
    def predict_with_confidence(self, x):
        """Get predictions with confidence from each model"""
        predictions = []
        confidences = []
        
        for model in self.models:
            with torch.no_grad():
                output = model(x)
                probs = torch.softmax(output, dim=1)
                confidence, pred = torch.max(probs, dim=1)
                predictions.append(pred)
                confidences.append(confidence)
        
        # Ensemble prediction
        ensemble_pred = torch.mode(torch.stack(predictions), dim=0)[0]
        ensemble_conf = torch.mean(torch.stack(confidences), dim=0)
        
        return ensemble_pred, ensemble_conf

def create_model(model_type: str, num_classes: int = 2, pretrained: bool = True) -> nn.Module:
    """
    Factory function to create models
    
    Args:
        model_type: Type of model to create
        num_classes: Number of output classes
        pretrained: Whether to use pretrained weights
        
    Returns:
        Created model
    """
    if model_type == "chest_xray":
        return ChestXRayClassifier(num_classes, pretrained)
    elif model_type == "brain_mri":
        return BrainMRIClassifier(num_classes, pretrained)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")

def load_pretrained_model(model_path: str, model_type: str, num_classes: int = 2) -> nn.Module:
    """
    Load pretrained model from checkpoint
    
    Args:
        model_path: Path to model checkpoint
        model_type: Type of model
        num_classes: Number of classes
        
    Returns:
        Loaded model
    """
    model = create_model(model_type, num_classes)
    
    checkpoint = torch.load(model_path, map_location='cpu')
    
    # Handle different checkpoint formats
    if 'model_state_dict' in checkpoint:
        model.load_state_dict(checkpoint['model_state_dict'])
    elif 'state_dict' in checkpoint:
        model.load_state_dict(checkpoint['state_dict'])
    else:
        model.load_state_dict(checkpoint)
    
    model.eval()
    return model

# Model testing and validation
def test_model(model: nn.Module, test_loader, device: str = 'cpu'):
    """
    Test model performance
    
    Args:
        model: Model to test
        test_loader: Test data loader
        device: Device to run on
        
    Returns:
        Test accuracy and predictions
    """
    model.eval()
    correct = 0
    total = 0
    all_predictions = []
    all_labels = []
    
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            
            all_predictions.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    
    accuracy = 100 * correct / total
    return accuracy, all_predictions, all_labels

if __name__ == "__main__":
    # Test model creation
    print("Testing model creation...")
    
    # Create chest X-ray model
    chest_model = create_model("chest_xray")
    chest_info = chest_model.get_model_info()
    print(f"Chest X-ray model: {chest_info}")
    
    # Create brain MRI model
    brain_model = create_model("brain_mri")
    brain_info = brain_model.get_model_info()
    print(f"Brain MRI model: {brain_info}")
    
    # Test forward pass
    dummy_input = torch.randn(1, 3, 224, 224)
    
    with torch.no_grad():
        chest_output = chest_model(dummy_input)
        brain_output = brain_model(dummy_input)
    
    print(f"Chest model output shape: {chest_output.shape}")
    print(f"Brain model output shape: {brain_output.shape}")
    
    print("Model testing completed successfully!")
