import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';

const ImageUploadScreen = () => {
  const navigate = useNavigate();
  const [selectedImage, setSelectedImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const title = '🧠 Brain MRI Analysis';

  const handleImageSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedImage(file);
      setError('');
    }
  };

  const analyzeImage = async () => {
    if (!selectedImage) {
      setError('⚠️ Please select a brain MRI image first');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('image', selectedImage);
      formData.append('image_type', 'brain_mri');

      const response = await axios.post('http://localhost:8001/api/predict', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // 60 second timeout
      });

      navigate('/result', {
        state: {
          result: response.data,
          imageUri: URL.createObjectURL(selectedImage),
          imageType: 'brain_mri',
        },
      });
    } catch (err) {
      if (err.code === 'ECONNABORTED') {
        setError('⏱️ Analysis timed out. Please try again.');
      } else if (err.response?.status === 413) {
        setError('📁 Image too large. Please use a smaller image.');
      } else if (err.response?.status === 415) {
        setError('📷 Unsupported image format. Please use JPG or PNG.');
      } else {
        setError('❌ Failed to analyze image. Please check your connection and try again.');
      }
      console.error('Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="header">
        <h1 className="title">{title}</h1>
        <p className="subtitle">🔬 Upload a brain MRI image for advanced AI-powered tumor detection</p>
      </div>
      
      <div className="card">
        <div className="upload-section">
          {selectedImage && (
            <div className="image-preview-container">
              <img 
                src={URL.createObjectURL(selectedImage)} 
                alt="Selected brain MRI image" 
                className="image-preview"
              />
              <div className="image-info">
                <h4>📋 Image Selected</h4>
                <p>📁 {selectedImage.name}</p>
                <p>📏 {(selectedImage.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
            </div>
          )}
          
          <div className="upload-controls">
            <div className="file-input">
              <input 
                type="file" 
                accept="image/jpeg,image/png,image/jpg" 
                onChange={handleImageSelect}
                disabled={loading}
                id="mri-upload"
              />
              <label htmlFor="mri-upload" className="file-label">
                📷 Choose Brain MRI Image
              </label>
              <button 
                type="button"
                onClick={() => setSelectedImage(null)}
                className="button secondary"
              >
                🔄 Choose Different Image
              </button>
            </div>
            <div className="upload-tips">
              <h5>💡 Tips for Best Results:</h5>
              <ul>
                <li>✅ Use high-quality MRI scans</li>
                <li>✅ Ensure clear tumor visibility</li>
                <li>✅ JPG or PNG format preferred</li>
                <li>✅ File size under 10MB</li>
              </ul>
            </div>
          </div>
        </div>
        
        {error && (
          <div className="error">
            {error}
          </div>
        )}
        
        <div className="action-buttons">
          <button 
            onClick={analyzeImage} 
            disabled={loading || !selectedImage}
            className="button brain-mri"
          >
            {loading ? '🔄 Analyzing MRI...' : '🧠 Analyze for Tumors'}
          </button>
          
          <Link to="/" className="button secondary">
            🏠 Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ImageUploadScreen;
