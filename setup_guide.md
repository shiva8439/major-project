# AI Medical Image Diagnosis System - Setup Guide

## Prerequisites
- Python 3.10+
- React Native development environment
  - Node.js 22.11.0+
  - React Native CLI
  - Android Studio (for Android development)
  - Xcode (for iOS development - macOS only)
- VS Code with React Native/Python extensions
- Git

## Backend Setup (FastAPI + PyTorch)
1. `cd backend`
2. `python -m venv venv`
3. `venv\\Scripts\\activate` (Windows)
4. `pip install -r requirements.txt`
5. Download sample models to `backend/models/` (or use demo random weights):
   - chest_xray_model.pth
   - brain_mri_model.pth
6. `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

Test: http://localhost:8000/docs (Swagger UI)
- POST /api/predict
- GET /api/history

## Frontend Setup (React Native)
1. `cd frontend`
2. `npm install`
3. Ensure backend running on localhost:8000
4. `npx react-native run-android` (for Android)
   OR
   `npx react-native run-ios` (for iOS - macOS only)

## Features
- Image upload (gallery/camera)
- Chest X-ray/Brain MRI selector
- AI prediction + confidence
- Grad-CAM heatmap
- Prediction history
- Cross-platform (iOS/Android)

## Sample Test Images
Use `sample_images/` - replace placeholders with real medical JPGs (224x224 recommended)

## Troubleshooting
- **No models**: Uses random demo - predictions random until .pth files added
- **GPU**: Torch auto-detects CUDA
- **React Native permissions**: Camera and storage permissions required
- **CORS**: Allowed for localhost
- **Metro bundler**: Run `npx react-native start` if bundler issues

## Production
- Add real fine-tuned .pth models
- Deploy backend: Docker/Heroku
- Frontend: `npx react-native build-android` or `npx react-native build-ios`
