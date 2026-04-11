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
    response = requests.post('http://localhost:8000/api/predict', files=files, data=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
