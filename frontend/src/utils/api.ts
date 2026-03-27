import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Enable CORS credentials
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any request modifications here
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Handle unauthorized
      console.error('Unauthorized access')
    } else if (error.response?.status === 500) {
      // Handle server error
      console.error('Server error')
    } else if (error.code === 'ECONNABORTED') {
      // Handle timeout
      console.error('Request timeout')
    }
    
    return Promise.reject(error)
  }
)

// API endpoints
export const endpoints = {
  predict: '/api/predict',
  chat: '/api/chat',
  history: '/api/history',
  health: '/api/health',
  heatmap: (fileId: string) => `/api/heatmap/${fileId}`,
}

export default api
