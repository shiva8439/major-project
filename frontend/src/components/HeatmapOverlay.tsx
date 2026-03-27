import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Eye, EyeOff, Download, Maximize2 } from 'lucide-react'
import { useLanguage } from '../contexts/LanguageContext'
import toast from 'react-hot-toast'

interface HeatmapOverlayProps {
  originalImage: string
  heatmapImage?: string | null
  title?: string
}

const HeatmapOverlay: React.FC<HeatmapOverlayProps> = ({
  originalImage,
  heatmapImage,
  title = 'Grad-CAM Heatmap'
}) => {
  const { t } = useLanguage()
  const [showHeatmap, setShowHeatmap] = useState(true)
  const [isFullscreen, setIsFullscreen] = useState(false)

  const handleDownload = async () => {
    if (!heatmapImage) return

    try {
      const response = await fetch(heatmapImage)
      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      
      const a = document.createElement('a')
      a.href = url
      a.download = `heatmap-${Date.now()}.png`
      a.click()
      
      URL.revokeObjectURL(url)
      toast.success('Heatmap downloaded successfully')
    } catch (error) {
      toast.error('Failed to download heatmap')
    }
  }

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen)
  }

  if (!heatmapImage) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          {t('home.heatmap.title')}
        </h3>
        <div className="text-center py-8">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Eye className="w-8 h-8 text-gray-400" />
          </div>
          <p className="text-gray-600">
            {t('home.heatmap.subtitle')}
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Heatmap will be generated after analysis
          </p>
        </div>
      </div>
    )
  }

  return (
    <>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-lg shadow-lg p-6"
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            {title}
          </h3>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowHeatmap(!showHeatmap)}
              className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              title={showHeatmap ? 'Hide heatmap' : 'Show heatmap'}
            >
              {showHeatmap ? (
                <EyeOff className="w-4 h-4" />
              ) : (
                <Eye className="w-4 h-4" />
              )}
            </button>
            
            <button
              onClick={toggleFullscreen}
              className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              title="Toggle fullscreen"
            >
              <Maximize2 className="w-4 h-4" />
            </button>
            
            <button
              onClick={handleDownload}
              className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              title={t('common.download')}
            >
              <Download className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Image Container */}
        <div className="relative rounded-lg overflow-hidden bg-gray-100">
          <img
            src={originalImage}
            alt="Original medical image"
            className="w-full h-auto object-contain"
          />
          
          {showHeatmap && (
            <motion.img
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.7 }}
              transition={{ duration: 0.3 }}
              src={heatmapImage}
              alt="Grad-CAM heatmap overlay"
              className="absolute top-0 left-0 w-full h-full object-contain mix-blend-multiply"
            />
          )}
        </div>

        {/* Legend */}
        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-blue-500 rounded"></div>
                <span className="text-gray-700">Low attention</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-red-500 rounded"></div>
                <span className="text-gray-700">High attention</span>
              </div>
            </div>
            
            <div className="text-gray-600">
              {showHeatmap ? 'Overlay visible' : 'Overlay hidden'}
            </div>
          </div>
        </div>

        {/* Info */}
        <div className="mt-4 text-sm text-gray-600">
          <p>
            <strong>Grad-CAM</strong> highlights the regions the AI model focused on when making its prediction.
            Warmer colors (red/orange) indicate areas of higher importance.
          </p>
        </div>
      </motion.div>

      {/* Fullscreen Modal */}
      {isFullscreen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-4"
          onClick={toggleFullscreen}
        >
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            exit={{ scale: 0.8 }}
            className="relative max-w-6xl max-h-full"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={toggleFullscreen}
              className="absolute top-4 right-4 p-2 bg-white rounded-full shadow-lg hover:bg-gray-100 transition-colors z-10"
            >
              <EyeOff className="w-5 h-5 text-gray-700" />
            </button>
            
            <div className="bg-white rounded-lg overflow-hidden">
              <div className="p-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">
                  {title} - Fullscreen
                </h3>
              </div>
              
              <div className="p-4">
                <div className="relative rounded-lg overflow-hidden bg-gray-100">
                  <img
                    src={originalImage}
                    alt="Original medical image"
                    className="w-full h-auto max-h-[70vh] object-contain"
                  />
                  
                  {showHeatmap && (
                    <img
                      src={heatmapImage}
                      alt="Grad-CAM heatmap overlay"
                      className="absolute top-0 left-0 w-full h-full max-h-[70vh] object-contain mix-blend-multiply"
                    />
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </>
  )
}

export default HeatmapOverlay
