import React from 'react';
import { useLocation, Link } from 'react-router-dom';

const ResultScreen = () => {
  const location = useLocation();
  const { result, imageUri, imageType } = location.state || {};

  if (!result) {
    return (
      <div className="container">
        <div className="card">
          <h2>No Results Available</h2>
          <Link to="/" className="button">
            Back to Home
          </Link>
        </div>
      </div>
    );
  }

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'confidence-high';
    if (confidence >= 0.6) return 'confidence-medium';
    return 'confidence-low';
  };

  const getConfidenceText = (confidence) => {
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.6) return 'Medium';
    return 'Low';
  };

  const getTumorTypeInfo = (prediction) => {
    const tumorTypes = {
      'Glioma': {
        description: 'Tumor arising from glial cells',
        severity: 'High',
        color: '#e74c3c'
      },
      'Meningioma': {
        description: 'Tumor arising from meninges',
        severity: 'Medium',
        color: '#f39c12'
      },
      'Pituitary Tumor': {
        description: 'Tumor of the pituitary gland',
        severity: 'Medium',
        color: '#3498db'
      },
      'Metastasis': {
        description: 'Secondary tumor from other cancer',
        severity: 'Very High',
        color: '#c0392b'
      },
      'Normal': {
        description: 'No tumor detected',
        severity: 'None',
        color: '#27ae60'
      },
      'Pneumonia': {
        description: 'Lung infection',
        severity: 'Medium',
        color: '#f39c12'
      },
      'COVID-19': {
        description: 'COVID-19 infection',
        severity: 'High',
        color: '#e74c3c'
      },
      'Tuberculosis': {
        description: 'Bacterial lung infection',
        severity: 'Medium',
        color: '#e67e22'
      }
    };
    
    return tumorTypes[prediction] || { description: 'Unknown condition', severity: 'Unknown', color: '#95a5a6' };
  };

  const tumorInfo = getTumorTypeInfo(result.prediction);

  return (
    <div className="container">
      <div className="header">
        <h1 className="title">Professional Analysis Results</h1>
        <p className="subtitle">AI-Powered Medical Image Diagnosis</p>
      </div>

      <div className="card">
        <h3>Original Medical Image</h3>
        <img src={imageUri} alt="Medical image" className="image-preview" />
      </div>

      <div className="result-card">
        <h3>Diagnosis Report</h3>
        
        <div className="analysis-stats">
          <div className="stat-card">
            <div className="stat-value">{imageType === 'chest_xray' ? 'Chest X-ray' : 'Brain MRI'}</div>
            <div className="stat-label">Image Type</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-value">{(result.confidence * 100).toFixed(1)}%</div>
            <div className="stat-label">Confidence Level</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-value" style={{ fontSize: '1.5rem' }}>{result.prediction}</div>
            <div className="stat-label">Primary Diagnosis</div>
          </div>
        </div>

        <div className="result-item">
          <span className="result-label">Condition Detected:</span>
          <span className="result-value">
            {result.prediction}
            {imageType === 'brain_mri' && result.prediction !== 'Normal' && (
              <span className="tumor-type">Tumor</span>
            )}
          </span>
        </div>

        <div className="result-item">
          <span className="result-label">Confidence:</span>
          <span className={`confidence-badge ${getConfidenceColor(result.confidence)}`}>
            {(result.confidence * 100).toFixed(1)}% ({getConfidenceText(result.confidence)})
          </span>
        </div>

        <div className="result-item">
          <span className="result-label">Description:</span>
          <span className="result-value" style={{ fontSize: '0.95rem' }}>
            {tumorInfo.description}
          </span>
        </div>

        <div className="result-item">
          <span className="result-label">Severity:</span>
          <span className="result-value" style={{ color: tumorInfo.color, fontWeight: '700' }}>
            {tumorInfo.severity}
          </span>
        </div>
      </div>

      {result.heatmap_url && (
        <div className="card">
          <h3>AI Attention Heatmap</h3>
          <p style={{ color: '#666', marginBottom: '20px' }}>
            This heatmap shows which areas the AI focused on when detecting: <strong>{result.prediction}</strong>
          </p>
          <p style={{ color: '#888', fontSize: '0.9rem', marginBottom: '20px' }}>
            {imageType === 'brain_mri' && result.prediction !== 'Normal' 
              ? `The AI identified attention patterns consistent with ${tumorInfo.description.toLowerCase()}.`
              : imageType === 'brain_mri' && result.prediction === 'Normal'
              ? 'The AI shows distributed attention with no specific focus areas, indicating normal findings.'
              : 'The AI highlights regions of interest in the chest X-ray for the detected condition.'
            }
          </p>
          <img src={`http://localhost:8000${result.heatmap_url}`} alt="Heatmap visualization" className="image-preview" />
          
          <div style={{ marginTop: '20px', padding: '15px', background: '#f8f9fa', borderRadius: '10px' }}>
            <h4 style={{ color: '#555', marginBottom: '10px' }}>How to Read This Heatmap:</h4>
            <ul style={{ textAlign: 'left', color: '#666', lineHeight: '1.6' }}>
              <li><strong>Red/Yellow areas:</strong> High AI attention - most important for diagnosis</li>
              <li><strong>Blue/Green areas:</strong> Lower AI attention - less relevant</li>
              <li><strong>Different patterns:</strong> Each condition shows unique attention patterns</li>
            </ul>
          </div>
        </div>
      )}

      <div className="card" style={{ background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)' }}>
        <h3>Medical Disclaimer</h3>
        <p style={{ color: '#666', lineHeight: '1.6' }}>
          This AI analysis is for informational purposes only and should not be used as a substitute for professional medical diagnosis. 
          Always consult with qualified healthcare professionals for medical decisions.
        </p>
      </div>

      <div style={{ textAlign: 'center', marginTop: '40px' }}>
        <Link to="/" className="button chest-xray" style={{ marginRight: '15px' }}>
          New Analysis
        </Link>
        <Link to="/history" className="button history">
          View History
        </Link>
      </div>
    </div>
  );
};

export default ResultScreen;
