import requests
import io
from PIL import Image
import numpy as np

# Create a simple test image
test_image = Image.new('RGB', (224, 224), color='red')
img_bytes = io.BytesIO()
test_image.save(img_bytes, format='JPEG')
img_bytes.seek(0)

# Test the API
files = {'image': ('test.jpg', img_bytes, 'image/jpeg')}
data = {'image_type': 'brain_mri'}

try:
    # Get prediction
    response = requests.post('http://localhost:8000/api/predict', files=files, data=data)
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Prediction: {result}")
    
    # Test heatmap
    if 'heatmap_url' in result:
        heatmap_response = requests.get(f"http://localhost:8000{result['heatmap_url']}")
        print(f"Heatmap Status: {heatmap_response.status_code}")
        print(f"Heatmap Size: {len(heatmap_response.content)} bytes")
        
        # Save heatmap to check
        with open('test_heatmap.jpg', 'wb') as f:
            f.write(heatmap_response.content)
        print("Heatmap saved as test_heatmap.jpg")
    
except Exception as e:
    print(f"Error: {e}")
