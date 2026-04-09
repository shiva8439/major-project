import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';

const ImageUploadScreen = () => {
  const { imageType } = useParams();
  const navigate = useNavigate();
  const [selectedImage, setSelectedImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const title = imageType === 'chest_xray' ? 'Chest X-ray Analysis' : 'Brain MRI Analysis';

  const handleImageSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedImage(file);
      setError('');
    }
  };

  const analyzeImage = async () => {
    if (!selectedImage) {
      setError('Please select an image first');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('image', selectedImage);
      formData.append('image_type', imageType);

      const response = await axios.post('http://localhost:8000/api/predict', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      navigate('/result', {
        state: {
          result: response.data,
          imageUri: URL.createObjectURL(selectedImage),
          imageType,
        },
      });
    } catch (err) {
      setError('Failed to analyze image. Please try again.');
      console.error('Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="header">
        <h1 className="title">{title}</h1>
      </div>

      <div className="card">
        <div className="file-input">
          <input
            type="file"
            id="image-upload"
            accept="image/*"
            onChange={handleImageSelect}
          />
          <label htmlFor="image-upload" className="file-label">
            Choose Medical Image
          </label>
        </div>

        {selectedImage && (
          <div>
            <h3>Selected Image:</h3>
            <img
              src={URL.createObjectURL(selectedImage)}
              alt="Selected medical image"
              className="image-preview"
            />
            <div style={{ marginTop: '20px' }}>
              <button
                className="button"
                onClick={analyzeImage}
                disabled={loading}
                style={{ marginRight: '10px' }}
              >
                {loading ? 'Analyzing...' : 'Analyze Image'}
              </button>
              <button
                className="button secondary"
                onClick={() => setSelectedImage(null)}
              >
                Choose Different Image
              </button>
            </div>
          </div>
        )}

        {error && <div className="error">{error}</div>}
      </div>

      <div style={{ textAlign: 'center', marginTop: '20px' }}>
        <Link to="/" className="button secondary">
          Back to Home
        </Link>
      </div>
    </div>
  );
};

export default ImageUploadScreen;
