# AI Models for Medical Diagnosis

This directory contains the AI models and training scripts for the medical diagnosis system.

## Directory Structure

```
models/
├── training/                    # Training scripts and utilities
│   ├── train.py                # Main training script
│   ├── dataset.py              # Dataset loader
│   ├── data_augmentation.py    # Data augmentation techniques
│   └── model.py                # Model architectures
├── inference/                  # Inference utilities
│   ├── model_loader.py         # Model loading utilities
│   ├── predictor.py            # Main prediction class
│   └── grad_cam.py             # Grad-CAM implementation
└── README.md                   # This file
```

## Model Types

### 1. Chest X-ray Classification
- **Architecture**: ResNet50 with custom classifier head
- **Classes**: Normal, Pneumonia
- **Input Size**: 224x224 RGB images
- **Pretrained**: ImageNet weights

### 2. Brain MRI Classification
- **Architecture**: EfficientNet-B0 with custom classifier head
- **Classes**: Normal, Tumor
- **Input Size**: 224x224 RGB images
- **Pretrained**: ImageNet weights

## Training

### Prerequisites
```bash
pip install torch torchvision scikit-learn matplotlib pillow opencv-python
```

### Dataset Structure
Organize your dataset as follows:

```
data/
├── chest_xray/
│   ├── train/
│   │   ├── Normal/
│   │   └── Pneumonia/
│   ├── val/
│   │   ├── Normal/
│   │   └── Pneumonia/
│   └── test/
│       ├── Normal/
│       └── Pneumonia/
└── brain_mri/
    ├── train/
    │   ├── Normal/
    │   └── Tumor/
    ├── val/
    │   ├── Normal/
    │   └── Tumor/
    └── test/
        ├── Normal/
        └── Tumor/
```

### Training Commands

#### Train Chest X-ray Model
```bash
cd models/training
python train.py --model_type chest_xray --data_dir ../../data --epochs 50
```

#### Train Brain MRI Model
```bash
cd models/training
python train.py --model_type brain_mri --data_dir ../../data --epochs 30
```

### Training Features
- **Data Augmentation**: Medical-specific augmentations
- **Learning Rate Scheduling**: ReduceLROnPlateau
- **Early Stopping**: Based on validation accuracy
- **Model Checkpointing**: Save best models
- **Training Visualization**: Loss and accuracy curves
- **Performance Metrics**: Classification reports and confusion matrices

## Inference

### Model Loading
```python
from models.inference.model_loader import model_loader

# Load models
model_loader.load_all_models(
    chest_model_path="models/inference/chest_xray_model.pth",
    brain_model_path="models/inference/brain_mri_model.pth"
)
```

### Making Predictions
```python
from models.inference.predictor import predictor

# Predict on image
with open("image.jpg", "rb") as f:
    image_data = f.read()

result = predictor.predict(image_data, "chest_xray")
print(f"Prediction: {result['prediction']}")
print(f"Confidence: {result['confidence_percentage']}%")
```

### Grad-CAM Visualization
```python
from models.inference.grad_cam import grad_cam_generator

# Generate heatmap
model = model_loader.get_model("chest_xray")
input_tensor, original_image = predictor.preprocess_image(image_data)

heatmap_data = grad_cam_generator.generate_heatmap_data(
    model, input_tensor, original_image, "chest_xray", "Pneumonia"
)
```

## Model Performance

### Expected Performance
- **Chest X-ray**: ~95% accuracy on test set
- **Brain MRI**: ~92% accuracy on test set

### Metrics
- Accuracy
- Precision, Recall, F1-Score
- ROC-AUC
- Confusion Matrix

## Data Augmentation

### Medical-Specific Augmentations
- **Brightness Adjustment**: ±20%
- **Contrast Enhancement**: ±20%
- **Subtle Gaussian Blur**: Radius 0.1-0.5
- **Small Rotations**: ±5° for X-ray, ±3° for MRI
- **Minor Translations**: ±5% for X-ray, ±2% for MRI
- **Histogram Equalization**: CLAHE for contrast enhancement

### Advanced Techniques
- **Elastic Transformations**: For simulating tissue deformations
- **Noise Injection**: Gaussian noise for robustness
- **Mixup**: Linear interpolation between samples

## Grad-CAM Explainability

### Features
- **Layer Selection**: Automatic target layer detection
- **Heatmap Generation**: Class-specific activation maps
- **Overlay Visualization**: Heatmap overlay on original image
- **Region Analysis**: Bounding boxes for important regions
- **Fallback Mechanism**: Gradient-based visualization when Grad-CAM fails

### Target Layers
- **ResNet50**: `layer4` (final residual block)
- **EfficientNet-B0**: `features.8` (final feature layer)

## Model Configuration

### Configuration File (model_config.json)
```json
{
  "chest_xray": {
    "num_classes": 2,
    "pretrained": true,
    "class_names": ["Normal", "Pneumonia"],
    "input_size": [224, 224],
    "normalization": {
      "mean": [0.485, 0.456, 0.406],
      "std": [0.229, 0.224, 0.225]
    }
  },
  "brain_mri": {
    "num_classes": 2,
    "pretrained": true,
    "class_names": ["Normal", "Tumor"],
    "input_size": [224, 224],
    "normalization": {
      "mean": [0.485, 0.456, 0.406],
      "std": [0.229, 0.224, 0.225]
    }
  }
}
```

## Best Practices

### Training
1. **Data Quality**: Ensure high-quality, labeled medical images
2. **Class Balance**: Handle imbalanced datasets with appropriate techniques
3. **Validation**: Use separate validation set for hyperparameter tuning
4. **Regularization**: Apply dropout and weight decay
5. **Monitoring**: Track training metrics and visualizations

### Inference
1. **Preprocessing**: Apply same transforms as training
2. **Model Warm-up**: Initialize models to reduce first inference latency
3. **Batch Processing**: Use batch inference for multiple images
4. **Error Handling**: Graceful fallback for failed predictions
5. **Quality Metrics**: Validate prediction confidence and processing time

### Deployment
1. **Model Versioning**: Track model versions and performance
2. **Monitoring**: Log predictions and errors
3. **Scaling**: Consider model quantization for deployment
4. **Security**: Validate input images and handle malicious inputs
5. **Compliance**: Ensure medical data privacy and regulations

## Troubleshooting

### Common Issues
1. **CUDA Out of Memory**: Reduce batch size or model complexity
2. **Poor Performance**: Check data quality and augmentation
3. **Grad-CAM Failures**: Verify layer names and model architecture
4. **Slow Inference**: Optimize model and use appropriate hardware

### Debugging
- Enable logging for detailed error messages
- Use sample datasets for testing
- Visualize intermediate outputs
- Monitor GPU memory usage

## Future Improvements

1. **Multi-class Classification**: Extend to more disease categories
2. **3D Medical Images**: Support for CT and MRI volumes
3. **Ensemble Methods**: Combine multiple models for better performance
4. **Active Learning**: Interactive model improvement
5. **Federated Learning**: Privacy-preserving training across institutions
