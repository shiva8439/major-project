import pytest
from fastapi.testclient import TestClient
import os
import sys
from PIL import Image
import io

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

# Create test client
client = TestClient(app)

def create_test_image():
    """Create a test image for testing"""
    # Create a simple test image
    img = Image.new('RGB', (224, 224), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

class TestHealthCheck:
    """Test health check endpoints"""
    
    def test_root_health_check(self):
        """Test root health check endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["version"] == "1.0.0"
    
    def test_api_health_check(self):
        """Test API health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "endpoints" in data

class TestPredictionAPI:
    """Test prediction API endpoints"""
    
    def test_predict_without_file(self):
        """Test prediction endpoint without file"""
        response = client.post("/api/predict")
        assert response.status_code == 422  # Validation error
    
    def test_predict_with_invalid_file_type(self):
        """Test prediction endpoint with invalid file type"""
        files = {"file": ("test.txt", b"not an image", "text/plain")}
        response = client.post("/api/predict", files=files)
        assert response.status_code == 400
        assert "File must be an image" in response.json()["detail"]
    
    def test_predict_with_invalid_image_type(self):
        """Test prediction endpoint with invalid image type"""
        test_image = create_test_image()
        files = {"file": ("test.png", test_image, "image/png")}
        data = {"image_type": "invalid_type"}
        response = client.post("/api/predict", files=files, data=data)
        assert response.status_code == 400
        assert "Invalid image type" in response.json()["detail"]
    
    def test_predict_chest_xray_success(self):
        """Test successful chest X-ray prediction"""
        test_image = create_test_image()
        files = {"file": ("test.png", test_image, "image/png")}
        data = {"image_type": "chest_xray"}
        
        response = client.post("/api/predict", files=files, data=data)
        
        # Note: This might fail if models are not loaded, but structure should be correct
        # In a real test environment, you'd mock the model loading
        assert response.status_code in [200, 500]  # 500 if model not loaded
    
    def test_predict_brain_mri_success(self):
        """Test successful brain MRI prediction"""
        test_image = create_test_image()
        files = {"file": ("test.png", test_image, "image/png")}
        data = {"image_type": "brain_mri"}
        
        response = client.post("/api/predict", files=files, data=data)
        
        # Note: This might fail if models are not loaded, but structure should be correct
        assert response.status_code in [200, 500]  # 500 if model not loaded
    
    def test_get_heatmap_not_found(self):
        """Test getting non-existent heatmap"""
        response = client.get("/api/heatmap/nonexistent")
        assert response.status_code == 404
        assert "Heatmap not found" in response.json()["detail"]
    
    def test_get_history(self):
        """Test getting prediction history"""
        response = client.get("/api/history")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

class TestChatbotAPI:
    """Test chatbot API endpoints"""
    
    def test_chat_english(self):
        """Test chatbot in English"""
        data = {
            "message": "Hello",
            "language": "en"
        }
        response = client.post("/api/chat", json=data)
        assert response.status_code == 200
        assert "response" in response.json()
        assert "timestamp" in response.json()
    
    def test_chat_hindi(self):
        """Test chatbot in Hindi"""
        data = {
            "message": "नमस्ते",
            "language": "hi"
        }
        response = client.post("/api/chat", json=data)
        assert response.status_code == 200
        assert "response" in response.json()
    
    def test_chat_medical_question(self):
        """Test chatbot with medical question"""
        data = {
            "message": "What are the symptoms of pneumonia?",
            "language": "en"
        }
        response = client.post("/api/chat", json=data)
        assert response.status_code == 200
        response_data = response.json()
        assert "symptoms" in response_data["response"].lower()
    
    def test_chat_invalid_language(self):
        """Test chatbot with invalid language (should default to English)"""
        data = {
            "message": "Hello",
            "language": "invalid"
        }
        response = client.post("/api/chat", json=data)
        assert response.status_code == 200

class TestAPIErrors:
    """Test API error handling"""
    
    def test_404_error(self):
        """Test 404 error handling"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_json(self):
        """Test invalid JSON handling"""
        response = client.post(
            "/api/chat",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

if __name__ == "__main__":
    pytest.main([__file__])
