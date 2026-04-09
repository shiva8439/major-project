import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const HistoryScreen = () => {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/history');
      setPredictions(response.data);
    } catch (err) {
      setError('Failed to load history. Please try again.');
      console.error('History error:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'confidence-high';
    if (confidence >= 0.6) return 'confidence-medium';
    return 'confidence-low';
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading history...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="header">
        <h1 className="title">Prediction History</h1>
      </div>

      <div className="card">
        {error && <div className="error">{error}</div>}
        
        {predictions.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <h3>No predictions yet</h3>
            <p>Start your first medical image analysis to see results here.</p>
            <Link to="/" className="button" style={{ marginTop: '20px' }}>
              Start New Analysis
            </Link>
          </div>
        ) : (
          <div>
            <h3>Previous Analyses</h3>
            {predictions.map((prediction) => (
              <div key={prediction.id} className="history-item">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <strong>{prediction.image_type === 'chest_xray' ? 'Chest X-ray' : 'Brain MRI'}</strong>
                    <br />
                    <span>{prediction.prediction}</span>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <span className={getConfidenceColor(prediction.confidence)}>
                      {(prediction.confidence * 100).toFixed(1)}%
                    </span>
                    <br />
                    <small style={{ color: '#666' }}>
                      {formatDate(prediction.timestamp)}
                    </small>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div style={{ textAlign: 'center', marginTop: '20px' }}>
        <Link to="/" className="button">
          New Analysis
        </Link>
      </div>
    </div>
  );
};

export default HistoryScreen;
