# AI Medical Diagnosis System - Project Structure

```
ai-medical-diagnosis/
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI application entry point
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── prediction.py         # Pydantic models
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── predict.py            # Prediction endpoint
│   │   │   └── chatbot.py            # Chatbot endpoint
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── model_loader.py       # Load AI models
│   │   │   ├── grad_cam.py           # Grad-CAM implementation
│   │   │   └── image_processor.py    # Image preprocessing
│   │   └── database.py               # Database connection (for history)
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_api.py               # API tests
│   ├── uploads/                      # Temporary upload directory
│   ├── requirements.txt              # Python dependencies
│   └── .env                          # Environment variables
│
├── frontend/                         # React Frontend
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   ├── src/
│   │   ├── components/
│   │   │   ├── ImageUpload.jsx       # Drag & drop upload
│   │   │   ├── ImagePreview.jsx      # Image preview component
│   │   │   ├── ResultDisplay.jsx     # Show prediction results
│   │   │   ├── HeatmapOverlay.jsx    # Grad-CAM overlay
│   │   │   ├── ChatBot.jsx           # AI chatbot interface
│   │   │   ├── LanguageSelector.jsx  # Language switcher
│   │   │   └── History.jsx           # Previous results
│   │   ├── pages/
│   │   │   ├── Home.jsx              # Main diagnosis page
│   │   │   └── About.jsx             # About/disclaimer page
│   │   ├── hooks/
│   │   │   ├── useTranslation.js     # Translation hook
│   │   │   └── useApi.js             # API calls
│   │   ├── utils/
│   │   │   ├── api.js                # API utilities
│   │   │   ├── translations.js       # Language translations
│   │   │   └── constants.js          # App constants
│   │   ├── App.jsx                   # Main App component
│   │   ├── index.js                  # React entry point
│   │   └── index.css                 # Global styles
│   ├── package.json                  # Node.js dependencies
│   └── tailwind.config.js            # Tailwind CSS config
│
├── models/                           # AI Models
│   ├── training/
│   │   ├── train.py                  # Model training script
│   │   ├── dataset.py                # Dataset loading
│   │   ├── data_augmentation.py      # Data augmentation
│   │   └── model.py                  # Model architecture
│   ├── inference/
│   │   ├── model_loader.py           # Load trained models
│   │   ├── predictor.py              # Inference logic
│   │   └── grad_cam.py               # Grad-CAM implementation
│   └── README.md                     # Model documentation
│
├── data/                             # Dataset storage
│   ├── chest_xray/                   # Chest X-ray dataset
│   └── brain_mri/                    # Brain MRI dataset
│
├── logs/                             # Application logs
│   ├── backend.log
│   └── training.log
│
├── docs/                             # Documentation
│   ├── API.md                        # API documentation
│   ├── DEPLOYMENT.md                 # Deployment guide
│   └── SETUP.md                      # Setup instructions
│
├── README.md                         # Project README
├── .gitignore                        # Git ignore file
└── docker-compose.yml                # Docker configuration
```

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PyTorch**: Deep learning framework
- **OpenCV**: Image processing
- **Pillow**: Image manipulation
- **SQLite**: Database for history (can be upgraded to PostgreSQL)
- **Uvicorn**: ASGI server

### Frontend
- **React.js**: Modern JavaScript library
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client
- **React Router**: Navigation
- **Lucide React**: Icons

### AI/ML
- **PyTorch**: Deep learning
- **ResNet50/EfficientNet**: Transfer learning models
- **Grad-CAM**: Model explainability
- **OpenCV**: Computer vision

### Deployment
- **Vercel**: Frontend hosting
- **Render**: Backend hosting
- **Docker**: Containerization

## Features

1. **Medical Image Analysis**
   - X-ray, MRI, CT scan support
   - Pneumonia detection
   - Brain tumor detection
   - Confidence scores

2. **Explainability**
   - Grad-CAM heatmaps
   - Visual explanations
   - Affected region highlighting

3. **User Interface**
   - Drag & drop upload
   - Real-time processing
   - Responsive design
   - Loading states

4. **Multilingual Support**
   - English and Hindi
   - Easy language switching

5. **AI Chatbot**
   - Medical Q&A
   - Basic health information

6. **History Feature**
   - Previous diagnoses
   - Result comparison

7. **Safety Features**
   - Medical disclaimer
   - Error handling
   - Input validation
