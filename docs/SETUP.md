# Setup Guide

This guide provides detailed instructions for setting up the AI Medical Diagnosis System on your local machine.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Backend Setup](#backend-setup)
3. [Frontend Setup](#frontend-setup)
4. [Model Setup](#model-setup)
5. [Database Setup](#database-setup)
6. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10, macOS 10.14, or Ubuntu 18.04+
- **Python**: 3.8 or higher
- **Node.js**: 16.0 or higher
- **RAM**: 8GB (16GB recommended)
- **Storage**: 10GB free space
- **GPU**: NVIDIA GPU with CUDA support (optional but recommended)

### Recommended Requirements
- **Operating System**: Windows 11, macOS 12, or Ubuntu 20.04+
- **Python**: 3.9 or higher
- **Node.js**: 18.0 or higher
- **RAM**: 16GB or higher
- **Storage**: 20GB free space
- **GPU**: NVIDIA RTX 3060 or better with 8GB+ VRAM

## Backend Setup

### 1. Install Python

#### Windows
```powershell
# Download Python from python.org
# Or use Chocolatey
choco install python

# Verify installation
python --version
pip --version
```

#### macOS
```bash
# Use Homebrew
brew install python3

# Verify installation
python3 --version
pip3 --version
```

#### Ubuntu/Debian
```bash
# Update package list
sudo apt update

# Install Python and development tools
sudo apt install python3 python3-pip python3-dev python3-venv

# Verify installation
python3 --version
pip3 --version
```

### 2. Create Virtual Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### 4. Install System Dependencies

#### Windows
```powershell
# Install Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Install CUDA (optional)
# Download from: https://developer.nvidia.com/cuda-downloads
```

#### macOS
```bash
# Install Xcode command line tools
xcode-select --install

# Install OpenMP (for some packages)
brew install libomp
```

#### Ubuntu/Debian
```bash
# Install system packages
sudo apt update
sudo apt install -y python3-dev build-essential
sudo apt install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1
sudo apt install -y libgstreamer1.0-dev gstreamer1.0-plugins-base
```

### 5. Environment Configuration

Create a `.env` file in the `backend` directory:

```env
# Development settings
DEBUG=True
SECRET_KEY=your-super-secret-key-change-this-in-production

# Database
DATABASE_URL=sqlite:///./medical_diagnosis.db

# Model paths
CHEST_XRAY_MODEL_PATH=../models/inference/chest_xray_model.pth
BRAIN_MRI_MODEL_PATH=../models/inference/brain_mri_model.pth

# Upload settings
MAX_FILE_SIZE=10485760
UPLOAD_DIR=./uploads

# CORS settings
ALLOWED_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# Optional: HuggingFace API for chatbot
HUGGINGFACE_API_KEY=your-huggingface-api-key
```

### 6. Start Backend Server

```bash
# From backend directory with activated virtual environment
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`

## Frontend Setup

### 1. Install Node.js

#### Windows
```powershell
# Download Node.js from nodejs.org
# Or use Chocolatey
choco install nodejs

# Verify installation
node --version
npm --version
```

#### macOS
```bash
# Use Homebrew
brew install node

# Verify installation
node --version
npm --version
```

#### Ubuntu/Debian
```bash
# Install Node.js using NodeSource
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
```

### 2. Install Dependencies

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

### 3. Environment Configuration

Create a `.env` file in the `frontend` directory:

```env
# API URL
VITE_API_URL=http://localhost:8000

# Optional: Enable/disable features
VITE_ENABLE_CHATBOT=true
VITE_ENABLE_HISTORY=true
VITE_ENABLE_HEATMAP=true
```

### 4. Start Frontend Server

```bash
# From frontend directory
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Model Setup

### Option 1: Use Pre-trained Models

1. Download pre-trained models from the releases page
2. Place them in `models/inference/` directory:
   ```
   models/inference/
   ├── chest_xray_model.pth
   └── brain_mri_model.pth
   ```

### Option 2: Train Your Own Models

1. **Prepare Dataset**
   - Download datasets from Kaggle
   - Organize as described in the main README

2. **Train Models**
   ```bash
   cd models/training
   
   # Train chest X-ray model
   python train.py --model_type chest_xray --data_dir ../../data --epochs 50
   
   # Train brain MRI model
   python train.py --model_type brain_mri --data_dir ../../data --epochs 30
   ```

3. **Verify Models**
   - Check that model files exist in `models/inference/`
   - Test with a sample image

## Database Setup

### SQLite (Default)

The application uses SQLite by default. No additional setup is required.

### PostgreSQL (Production)

1. **Install PostgreSQL**
   ```bash
   # Ubuntu/Debian
   sudo apt install postgresql postgresql-contrib
   
   # macOS
   brew install postgresql
   
   # Windows
   # Download from postgresql.org
   ```

2. **Create Database**
   ```bash
   # Switch to postgres user
   sudo -u postgres psql
   
   # Create database and user
   CREATE DATABASE medical_diagnosis;
   CREATE USER diagnosis_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE medical_diagnosis TO diagnosis_user;
   \q
   ```

3. **Update Environment**
   ```env
   DATABASE_URL=postgresql://diagnosis_user:your_password@localhost/medical_diagnosis
   ```

## Troubleshooting

### Common Issues

#### 1. Python Installation Issues

**Problem**: `python: command not found`
**Solution**: 
- Ensure Python is installed and in PATH
- Use `python3` instead of `python` on some systems

#### 2. Virtual Environment Issues

**Problem**: `venv\Scripts\activate: command not found`
**Solution**:
- On Windows, use PowerShell or Command Prompt
- Ensure you're in the correct directory
- Recreate virtual environment if needed

#### 3. Dependency Installation Issues

**Problem**: `error: Microsoft Visual C++ 14.0 is required`
**Solution**:
- Install Visual Studio Build Tools
- On Windows, use precompiled wheels when possible

#### 4. Port Already in Use

**Problem**: `Port 8000 is already in use`
**Solution**:
```bash
# Find process using port
netstat -tulpn | grep :8000  # Linux
netstat -ano | findstr :8000  # Windows

# Kill process
sudo kill -9 <PID>  # Linux
taskkill /PID <PID> /F  # Windows

# Or use different port
uvicorn app.main:app --port 8001
```

#### 5. CUDA/GPU Issues

**Problem**: `CUDA out of memory`
**Solution**:
- Reduce batch size in model configuration
- Use CPU instead of GPU for testing
- Close other GPU-intensive applications

#### 6. Frontend Build Issues

**Problem**: `Module not found: Can't resolve 'react'`
**Solution**:
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall dependencies
npm install
```

#### 7. CORS Issues

**Problem**: `CORS policy: No 'Access-Control-Allow-Origin' header`
**Solution**:
- Check backend CORS configuration
- Ensure frontend URL is in ALLOWED_ORIGINS
- Restart backend after configuration changes

### Performance Optimization

#### Backend
1. **Enable GPU Support**
   - Install CUDA toolkit
   - Install PyTorch with CUDA support
   - Monitor GPU usage with `nvidia-smi`

2. **Database Optimization**
   - Use PostgreSQL for production
   - Add proper indexes
   - Configure connection pooling

#### Frontend
1. **Build Optimization**
   - Use production build: `npm run build`
   - Enable code splitting
   - Optimize images and assets

2. **Browser Caching**
   - Implement proper cache headers
   - Use service workers for offline support

### Logging and Debugging

#### Backend Logs
```bash
# View logs in real-time
tail -f logs/backend.log

# Enable debug logging
export DEBUG=True
```

#### Frontend Debugging
- Open browser developer tools
- Check console for errors
- Use React DevTools for component inspection
- Network tab for API requests

### Getting Help

1. **Check Documentation**
   - Read the main README
   - Review API documentation at `/docs`
   - Check this troubleshooting guide

2. **Search Issues**
   - Check GitHub issues for similar problems
   - Search Stack Overflow with specific error messages

3. **Create Issue**
   - Provide detailed error information
   - Include system specifications
   - Share relevant logs and configuration

---

For additional support, please create an issue on the GitHub repository or contact the development team.
