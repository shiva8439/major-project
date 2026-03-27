# AI Medical Diagnosis System

A comprehensive full-stack AI-powered medical diagnosis system that analyzes medical images (X-rays, MRI, CT scans) to detect diseases like pneumonia or brain tumors using deep learning (CNNs) with explainability via Grad-CAM.

## 🌟 Features

- **AI-Powered Analysis**: Advanced deep learning models for accurate medical image analysis
- **Explainable AI**: Grad-CAM visualizations show what the AI is looking at
- **Multilingual Support**: Available in English and Hindi
- **AI Chatbot**: Medical assistant for basic health questions
- **Modern UI**: Responsive React frontend with Tailwind CSS
- **Real-time Processing**: Fast image analysis with confidence scores
- **History Tracking**: Store and view previous diagnosis results
- **Secure**: Built with best practices for medical data handling

## 🏗️ Project Structure

```
ai-medical-diagnosis/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── main.py        # Main FastAPI application
│   │   ├── models/        # Pydantic models
│   │   ├── routers/       # API endpoints
│   │   └── utils/         # Utilities (model loader, Grad-CAM, etc.)
│   ├── tests/             # Backend tests
│   └── requirements.txt   # Python dependencies
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── contexts/      # React contexts
│   │   └── utils/         # Frontend utilities
│   ├── package.json       # Node.js dependencies
│   └── tailwind.config.js # Tailwind CSS config
├── models/                 # AI Models
│   ├── training/          # Training scripts
│   └── inference/         # Inference utilities
├── data/                  # Dataset storage
├── docs/                  # Documentation
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ai-medical-diagnosis.git
cd ai-medical-diagnosis
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`

### 3. Frontend Setup

```bash
# Open a new terminal and navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 4. Access the Application

Open your browser and navigate to `http://localhost:3000`

## 📋 Detailed Setup Guide

### Backend Setup

1. **Environment Variables**
   Create a `.env` file in the `backend` directory:
   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///./medical_diagnosis.db
   CHEST_XRAY_MODEL_PATH=../models/inference/chest_xray_model.pth
   BRAIN_MRI_MODEL_PATH=../models/inference/brain_mri_model.pth
   UPLOAD_DIR=./uploads
   ALLOWED_ORIGINS=["http://localhost:3000"]
   ```

2. **Install System Dependencies**
   ```bash
   # On Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install python3-dev python3-pip
   sudo apt-get install libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1

   # On macOS (using Homebrew)
   brew install python3
   ```

3. **Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   The application uses SQLite by default. The database will be created automatically on first run.

### Frontend Setup

1. **Node.js Dependencies**
   ```bash
   npm install
   ```

2. **Environment Variables**
   Create a `.env` file in the `frontend` directory:
   ```env
   VITE_API_URL=http://localhost:8000
   ```

3. **Start Development Server**
   ```bash
   npm run dev
   ```

## 🤖 Model Training

### Dataset Preparation

1. **Download Datasets**
   - Chest X-ray: [Kaggle Chest X-ray Images](https://www.kaggle.com/paultimothymooney/chest-xray-pneumonia)
   - Brain MRI: [Kaggle Brain MRI Images](https://www.kaggle.com/datasets/masoudnickparvar/brain-mri-images-for-brain-tumor-detection)

2. **Organize Dataset**
   ```
   data/
   ├── chest_xray/
   │   ├── train/
   │   │   ├── Normal/
   │   │   └── Pneumonia/
   │   ├── val/
   │   └── test/
   └── brain_mri/
       ├── train/
       │   ├── Normal/
       │   └── Tumor/
       ├── val/
       └── test/
   ```

### Training Models

```bash
# Navigate to models directory
cd models/training

# Train chest X-ray model
python train.py --model_type chest_xray --data_dir ../../data --epochs 50

# Train brain MRI model
python train.py --model_type brain_mri --data_dir ../../data --epochs 30
```

### Model Files

Trained models will be saved to:
- `../models/inference/chest_xray_model.pth`
- `../models/inference/brain_mri_model.pth`

## 🌐 Deployment

### Backend Deployment (Render)

1. **Create Render Account**
   - Sign up at [Render](https://render.com)

2. **Deploy Backend**
   - Connect your GitHub repository
   - Create a new Web Service
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Add environment variables

### Frontend Deployment (Vercel)

1. **Create Vercel Account**
   - Sign up at [Vercel](https://vercel.com)

2. **Deploy Frontend**
   - Connect your GitHub repository
   - Configure root directory: `frontend`
   - Set build command: `npm run build`
   - Set output directory: `dist`
   - Add environment variables

### Docker Deployment

1. **Build Docker Images**
   ```bash
   # Backend
   docker build -t medical-diagnosis-backend ./backend
   
   # Frontend
   docker build -t medical-diagnosis-frontend ./frontend
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

## 🧪 Testing

### Backend Tests

```bash
cd backend
python -m pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 📊 API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Main Endpoints

- `POST /api/predict` - Analyze medical image
- `POST /api/chat` - Chat with medical assistant
- `GET /api/history` - Get prediction history
- `GET /api/health` - Health check

## 🔧 Configuration

### Backend Configuration

Key environment variables:
- `DEBUG`: Enable debug mode
- `SECRET_KEY`: JWT secret key
- `DATABASE_URL`: Database connection string
- `CHEST_XRAY_MODEL_PATH`: Path to chest X-ray model
- `BRAIN_MRI_MODEL_PATH`: Path to brain MRI model

### Frontend Configuration

Key environment variables:
- `VITE_API_URL`: Backend API URL

## 🛡️ Security Considerations

- All file uploads are validated for type and size
- Medical data is processed securely
- No sensitive data is stored in logs
- HTTPS recommended for production
- Regular security updates for dependencies

## 📝 Logging

### Backend Logs
- Location: `logs/backend.log`
- Includes request/response logs, errors, and model predictions

### Frontend Logs
- Browser console for development
- Error tracking for production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

**This is not a medical diagnosis tool.** The AI predictions provided by this system are for educational and research purposes only. Always consult a qualified healthcare professional for medical advice, diagnosis, or treatment.

## 🆘 Support

For issues and questions:
- Create an issue on GitHub
- Check the [documentation](docs/)
- Review the [FAQ](docs/FAQ.md)

## 🙏 Acknowledgments

- [PyTorch](https://pytorch.org/) for deep learning framework
- [FastAPI](https://fastapi.tiangolo.com/) for backend framework
- [React](https://reactjs.org/) for frontend framework
- [Tailwind CSS](https://tailwindcss.com/) for styling
- Medical image datasets from Kaggle and other open sources

---

**Built with ❤️ for better healthcare accessibility**
