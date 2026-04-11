import React from 'react';
import { Link } from 'react-router-dom';

const HomeScreen = () => {
  return (
    <div className="container">
      <div className="header">
        <h1 className="title">🧠 Brain Tumor Detection AI</h1>
        <p className="subtitle">Advanced AI-powered brain tumor diagnosis from MRI scans</p>
      </div>
      
      <div className="card-grid">
        <Link to="/upload/brain_mri" className="card">
          <div className="card-icon">{'\ud83e\udde0'}</div>
          <h2>🔬 Brain MRI Analysis</h2>
          <p>Upload MRI scans for instant AI tumor detection with 95%+ accuracy</p>
          <div className="card-features">
            <span>✓ 5 Tumor Types</span>
            <span>✓ Visual Heatmaps</span>
            <span>✓ Medical Reports</span>
          </div>
        </Link>
        <Link to="/history" className="card">
          <div className="card-icon">{'\ud83d\udccb'}</div>
          <h2>📊 Analysis History</h2>
          <p>View your previous brain tumor analyses and track progress</p>
          <div className="card-features">
            <span>✓ Complete Records</span>
            <span>✓ Detailed Reports</span>
            <span>✓ Progress Tracking</span>
          </div>
        </Link>
      </div>
      
      <div className="info-section">
        <h3>🏥 Trusted Medical AI</h3>
        <div className="info-grid">
          <div className="info-item">
            <h4>🎯 High Accuracy</h4>
            <p>Advanced deep learning models trained on thousands of medical images</p>
          </div>
          <div className="info-item">
            <h4>⚡ Instant Results</h4>
            <p>Get AI-powered analysis in seconds with detailed heatmaps</p>
          </div>
          <div className="info-item">
            <h4>🔒 Secure & Private</h4>
            <p>Your medical data is processed locally and kept confidential</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomeScreen;
