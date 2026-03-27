import React, { useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import { 
  Brain, 
  Stethoscope, 
  Activity
} from 'lucide-react'
import { useLanguage } from '../contexts/LanguageContext'
import ImageUpload from '../components/ImageUpload'
import ResultDisplay from '../components/ResultDisplay'
import HeatmapOverlay from '../components/HeatmapOverlay'
import ChatBot from '../components/ChatBot'
import { api, endpoints } from '../utils/api'
import toast from 'react-hot-toast'

const Home: React.FC = () => {
  const { t } = useLanguage()
  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  const [uploadedImageUrl, setUploadedImageUrl] = useState<string | null>(null)
  const [imageType, setImageType] = useState<'chest_xray' | 'brain_mri'>('brain_mri')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [heatmapUrl, setHeatmapUrl] = useState<string | null>(null)

  const handleImageUpload = (file: File) => {
    setSelectedImage(file)
    setUploadedImageUrl(URL.createObjectURL(file))
    setResult(null)
    setHeatmapUrl(null)
  }

  const handleRemoveImage = () => {
    if (uploadedImageUrl) {
      URL.revokeObjectURL(uploadedImageUrl)
    }
    setSelectedImage(null)
    setUploadedImageUrl(null)
    setResult(null)
    setHeatmapUrl(null)
  }

  const handleAnalyze = async () => {
    if (!selectedImage) {
      toast.error(t('msg.upload.image'))
      return
    }

    setIsAnalyzing(true)
    setResult(null)

    const formData = new FormData()
    formData.append('file', selectedImage)
    formData.append('image_type', imageType)

    try {
      const response = await api.post(endpoints.predict, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setResult(response.data)
      setHeatmapUrl(`${api.defaults.baseURL}${response.data.heatmap_url}`)
      toast.success(t('msg.analysis.success'))
    } catch (error: any) {
      console.error('Analysis error:', error)
      
      if (error.response?.status === 413) {
        toast.error(t('msg.file.too.large'))
      } else if (error.response?.status === 400) {
        toast.error(t('msg.invalid.file'))
      } else {
        toast.error(t('msg.server.error'))
      }
      
      setResult({
        success: false,
        error: error.response?.data?.detail || t('msg.analysis.error')
      })
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-12"
      >
        <div className="flex justify-center mb-6">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            className="p-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full"
          >
            <Brain className="w-12 h-12 text-white" />
          </motion.div>
        </div>
        
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
          {t('home.title')}
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          {t('home.subtitle')}
        </p>
      </motion.div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column - Upload and Analysis */}
        <div className="lg:col-span-2 space-y-8">
          {/* Image Type Selection */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-lg shadow-lg p-6"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {t('home.select.type')}
            </h3>
            
            <div className="grid grid-cols-2 gap-4">
              <button
                onClick={() => setImageType('chest_xray')}
                className={`p-4 rounded-lg border-2 transition-all ${
                  imageType === 'chest_xray'
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-200 hover:border-gray-300 text-gray-700'
                }`}
              >
                <Stethoscope className="w-8 h-8 mx-auto mb-2" />
                <div className="font-medium">{t('home.type.chest')}</div>
              </button>
              
              <button
                onClick={() => setImageType('brain_mri')}
                className={`p-4 rounded-lg border-2 transition-all ${
                  imageType === 'brain_mri'
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-200 hover:border-gray-300 text-gray-700'
                }`}
              >
                <Brain className="w-8 h-8 mx-auto mb-2" />
                <div className="font-medium">{t('home.type.brain')}</div>
              </button>
            </div>
          </motion.div>

          {/* Image Upload */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <ImageUpload
              onImageUpload={handleImageUpload}
              uploadedImage={uploadedImageUrl}
              onRemoveImage={handleRemoveImage}
              isAnalyzing={isAnalyzing}
            />
          </motion.div>

          {/* Analyze Button */}
          {uploadedImageUrl && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center"
            >
              <button
                onClick={handleAnalyze}
                disabled={isAnalyzing}
                className="px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-105"
              >
                {isAnalyzing ? (
                  <span className="flex items-center space-x-2">
                    <Activity className="w-5 h-5 animate-pulse" />
                    <span>{t('home.analyzing')}</span>
                  </span>
                ) : (
                  t('home.analyze')
                )}
              </button>
            </motion.div>
          )}

          {/* Results */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <ResultDisplay
              result={result}
              isAnalyzing={isAnalyzing}
              heatmapUrl={heatmapUrl}
            />
          </motion.div>

          {/* Heatmap */}
          {uploadedImageUrl && result?.success && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <HeatmapOverlay
                originalImage={uploadedImageUrl}
                heatmapImage={heatmapUrl}
              />
            </motion.div>
          )}
        </div>

        {/* Right Column - Chatbot */}
        <div className="lg:col-span-1">
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="sticky top-24"
          >
            <ChatBot />
          </motion.div>
        </div>
      </div>
    </div>
  )
}

export default Home
