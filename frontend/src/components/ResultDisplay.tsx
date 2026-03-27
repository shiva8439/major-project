import React from 'react'
import { motion } from 'framer-motion'
import { 
  CheckCircle, 
  XCircle, 
  Clock, 
  Brain,
  AlertTriangle,
  Download,
  Share2
} from 'lucide-react'
import { useLanguage } from '../contexts/LanguageContext'
import toast from 'react-hot-toast'

interface PredictionResult {
  prediction: string
  confidence: number
  confidence_percentage: number
  processing_time: number
  model_type: string
  heatmap_generated?: boolean
  heatmap_data?: {
    heatmap_overlay?: string
    cam_raw?: string
  }
  success: boolean
  error?: string
}

interface ResultDisplayProps {
  result: PredictionResult | null
  isAnalyzing: boolean
  heatmapUrl?: string | null
}

const ResultDisplay: React.FC<ResultDisplayProps> = ({ 
  result, 
  isAnalyzing, 
  heatmapUrl 
}) => {
  const { t } = useLanguage()

  const handleDownload = () => {
    if (!result) return
    
    const data = {
      prediction: result.prediction,
      confidence: result.confidence_percentage,
      processing_time: result.processing_time,
      model_type: result.model_type,
      timestamp: new Date().toISOString()
    }
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `medical-diagnosis-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
    
    toast.success('Results downloaded successfully')
  }

  const handleShare = async () => {
    if (!result) return
    
    try {
      const shareData = {
        title: 'AI Medical Diagnosis Result',
        text: `Prediction: ${result.prediction} with ${result.confidence_percentage}% confidence`,
        url: window.location.href
      }
      
      if (navigator.share) {
        await navigator.share(shareData)
      } else {
        // Fallback: copy to clipboard
        await navigator.clipboard.writeText(
          `Prediction: ${result.prediction} with ${result.confidence_percentage}% confidence`
        )
        toast.success('Results copied to clipboard')
      }
    } catch (error) {
      toast.error('Failed to share results')
    }
  }

  if (isAnalyzing) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-lg shadow-lg p-8"
      >
        <div className="flex flex-col items-center space-y-4">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="p-4 bg-blue-100 rounded-full"
          >
            <Brain className="w-8 h-8 text-blue-600" />
          </motion.div>
          
          <div className="text-center">
            <h3 className="text-lg font-semibold text-gray-900">
              {t('home.analyzing')}
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              AI is analyzing your medical image...
            </p>
          </div>
          
          <div className="w-full max-w-md">
            <div className="flex space-x-2">
              {[...Array(3)].map((_, i) => (
                <motion.div
                  key={i}
                  animate={{
                    scale: [1, 1.2, 1],
                    opacity: [0.5, 1, 0.5],
                  }}
                  transition={{
                    duration: 1.5,
                    repeat: Infinity,
                    delay: i * 0.2,
                  }}
                  className="flex-1 h-2 bg-blue-200 rounded-full"
                />
              ))}
            </div>
          </div>
        </div>
      </motion.div>
    )
  }

  if (!result) {
    return null
  }

  if (!result.success) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-red-50 border border-red-200 rounded-lg p-6"
      >
        <div className="flex items-start space-x-3">
          <XCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-lg font-semibold text-red-900">
              {t('common.error')}
            </h3>
            <p className="text-red-700 mt-1">
              {result.error || t('msg.analysis.error')}
            </p>
          </div>
        </div>
      </motion.div>
    )
  }

  const isPositive = result.prediction !== 'Normal'
  const confidenceColor = result.confidence >= 0.8 ? 'text-green-600' : 
                         result.confidence >= 0.6 ? 'text-yellow-600' : 'text-red-600'

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-lg shadow-lg p-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-gray-900">
          {t('home.results.title')}
        </h3>
        
        <div className="flex space-x-2">
          <button
            onClick={handleDownload}
            className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            title={t('common.download')}
          >
            <Download className="w-4 h-4" />
          </button>
          
          <button
            onClick={handleShare}
            className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            title={t('common.share')}
          >
            <Share2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Prediction Result */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Prediction Card */}
        <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            {isPositive ? (
              <AlertTriangle className="w-6 h-6 text-orange-600" />
            ) : (
              <CheckCircle className="w-6 h-6 text-green-600" />
            )}
            <span className="text-sm font-medium text-gray-600">
              {t('home.prediction')}
            </span>
          </div>
          
          <div className="text-2xl font-bold text-gray-900 mb-2">
            {result.prediction}
          </div>
          
          <div className={`text-lg font-medium ${confidenceColor}`}>
            {result.confidence_percentage}% {t('home.confidence')}
          </div>
        </div>

        {/* Processing Info */}
        <div className="bg-gray-50 rounded-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Clock className="w-6 h-6 text-gray-600" />
            <span className="text-sm font-medium text-gray-600">
              {t('home.processing.time')}
            </span>
          </div>
          
          <div className="text-2xl font-bold text-gray-900 mb-2">
            {result.processing_time}s
          </div>
          
          <div className="text-sm text-gray-600">
            Model: {result.model_type === 'chest_xray' ? 'Chest X-ray' : 'Brain MRI'}
          </div>
        </div>
      </div>

      {/* Confidence Bar */}
      <div className="mt-6">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-600">
            {t('home.confidence')}
          </span>
          <span className="text-sm font-medium text-gray-900">
            {result.confidence_percentage}%
          </span>
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-3">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${result.confidence_percentage}%` }}
            transition={{ duration: 1, ease: "easeOut" }}
            className={`h-3 rounded-full ${
              result.confidence >= 0.8 ? 'bg-green-500' :
              result.confidence >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
            }`}
          />
        </div>
      </div>

      {/* Disclaimer */}
      <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-sm text-yellow-800">
          <strong>Disclaimer:</strong> {t('home.disclaimer')}
        </p>
      </div>
    </motion.div>
  )
}

export default ResultDisplay
