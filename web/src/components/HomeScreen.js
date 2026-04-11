import React from 'react';
import { Link } from 'react-router-dom';

const HomeScreen = () => {
  return (
    <div className="container">
      <div className="header">
        <h1 className="title">AI Medical Diagnosis</h1>
        <p className="subtitle">Upload medical images for AI-powered diagnosis</p>
      </div>
      
      <div className="card-grid">
        <Link to="/upload/brain_mri" className="card">
          <div className="card-icon">{'\ud83e\udde0'}</div>
          <h2>Brain MRI Analysis</h2>
          <p>Detect brain tumors from MRI scans with AI</p>
        </Link>
        <Link to="/history" className="card">
          <div className="card-icon">{'\ud83d\udcbb'}</div>
          <h2>View History</h2>
          <p>View your previous diagnoses</p>
        </Link>
      </div>
    </div>
  );
};

export default HomeScreen;
