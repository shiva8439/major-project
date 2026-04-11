import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomeScreen from './components/HomeScreen';
import ImageUploadScreen from './components/ImageUploadScreen';
import ResultScreen from './components/ResultScreen';
import HistoryScreen from './components/HistoryScreen';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<HomeScreen />} />
          <Route path="/upload/brain_mri" element={<ImageUploadScreen />} />
          <Route path="/result" element={<ResultScreen />} />
          <Route path="/history" element={<HistoryScreen />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
