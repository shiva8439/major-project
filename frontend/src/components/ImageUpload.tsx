import React, { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion } from 'framer-motion'
import { Upload, X, Image as ImageIcon } from 'lucide-react'
import toast from 'react-hot-toast'

interface ImageUploadProps {
  onImageUpload: (file: File) => void
  uploadedImage: string | null
  onRemoveImage: () => void
  isAnalyzing: boolean
}

const ImageUpload: React.FC<ImageUploadProps> = ({
  onImageUpload,
  uploadedImage,
  onRemoveImage,
  isAnalyzing
}) => {
  const [dragActive, setDragActive] = useState(false)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    
    if (!file) return
    
    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast.error('Please upload a valid image file')
      return
    }
    
    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast.error('File size exceeds 10MB limit')
      return
    }
    
    onImageUpload(file)
    setDragActive(false)
  }, [onImageUpload])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    },
    multiple: false,
    disabled: isAnalyzing
  })

  const handleRemoveImage = () => {
    onRemoveImage()
  }

  if (uploadedImage) {
    return (
      <div className="relative">
        <div className="relative rounded-lg overflow-hidden shadow-lg">
          <img
            src={uploadedImage}
            alt="Uploaded medical image"
            className="w-full h-auto max-h-96 object-contain bg-gray-100"
          />
          
          {!isAnalyzing && (
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={handleRemoveImage}
              className="absolute top-4 right-4 p-2 bg-red-500 text-white rounded-full shadow-lg hover:bg-red-600 transition-colors"
            >
              <X className="w-4 h-4" />
            </motion.button>
          )}
        </div>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200
          ${isDragActive || isDragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400 bg-white'
          }
          ${isAnalyzing ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-50'}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center space-y-4">
          <motion.div
            animate={{
              scale: isDragActive ? [1, 1.1, 1] : 1,
            }}
            transition={{
              duration: 0.3,
              repeat: isDragActive ? Infinity : 0,
            }}
            className="p-4 bg-blue-100 rounded-full"
          >
            <Upload className="w-8 h-8 text-blue-600" />
          </motion.div>
          
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {isDragActive ? 'Drop your image here' : 'Upload Medical Image'}
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Drag and drop or click to browse
            </p>
            <p className="text-xs text-gray-500 mt-2">
              Supports: PNG, JPG, JPEG, GIF, BMP, WebP (Max 10MB)
            </p>
          </div>
        </div>
        
        {isDragActive && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="absolute inset-0 bg-blue-50 rounded-lg flex items-center justify-center"
          >
            <div className="text-center">
              <ImageIcon className="w-12 h-12 text-blue-600 mx-auto mb-2" />
              <p className="text-blue-600 font-medium">Release to upload</p>
            </div>
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}

export default ImageUpload
