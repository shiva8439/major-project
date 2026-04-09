import React from 'react';
import { Link } from 'react-router-dom';

const HomeScreen = () => {
  return (
    <div className="container">
      <div className="header">
        <h1 className="title">AI Medical Diagnosis</h1>
        <p className="subtitle">Upload medical images for AI-powered diagnosis</p>
      </div>
      
      <div className="card">
        <h2>Choose Analysis Type</h2>
        <div style={{ marginTop: '30px' }}>
          <Link to="/upload/chest_xray" className="button chest-xray">
            Chest X-ray Analysis
          </Link>
          <br />
          <Link to="/upload/brain_mri" className="button brain-mri">
            Brain MRI Analysis
          </Link>
          <br />
          <Link to="/history" className="button history">
            View History
          </Link>
        </div>
      </div>
    </div>
  );
};

export default HomeScreen;
