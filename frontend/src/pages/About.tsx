import React from 'react'
import { motion } from 'framer-motion'
import { 
  Brain, 
  Eye, 
  Globe, 
  MessageSquare,
  CheckCircle,
  ArrowRight,
  Upload,
  Cpu,
  FileText,
  ZoomIn
} from 'lucide-react'
import { useLanguage } from '../contexts/LanguageContext'

const About: React.FC = () => {
  const { t } = useLanguage()

  const features = [
    {
      icon: Brain,
      title: t('about.feature.ai'),
      description: t('about.feature.ai.desc'),
      color: 'from-blue-500 to-purple-600'
    },
    {
      icon: Eye,
      title: t('about.feature.explainable'),
      description: t('about.feature.explainable.desc'),
      color: 'from-green-500 to-teal-600'
    },
    {
      icon: Globe,
      title: t('about.feature.multilingual'),
      description: t('about.feature.multilingual.desc'),
      color: 'from-orange-500 to-red-600'
    },
    {
      icon: MessageSquare,
      title: t('about.feature.chatbot'),
      description: t('about.feature.chatbot.desc'),
      color: 'from-purple-500 to-pink-600'
    }
  ]

  const steps = [
    {
      icon: Upload,
      title: t('about.step1'),
      description: 'Drag and drop or browse to select your medical image'
    },
    {
      icon: Cpu,
      title: t('about.step2'),
      description: 'Our advanced AI models analyze the image for patterns'
    },
    {
      icon: FileText,
      title: t('about.step3'),
      description: 'Get instant results with confidence scores'
    },
    {
      icon: ZoomIn,
      title: t('about.step4'),
      description: 'View Grad-CAM heatmaps to understand the AI\'s focus'
    }
  ]

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-16"
      >
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
          {t('about.title')}
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          {t('about.subtitle')}
        </p>
      </motion.div>

      {/* Features Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="mb-16"
      >
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          {t('about.features.title')}
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 + index * 0.1 }}
                className="bg-white rounded-lg shadow-lg p-6 hover-lift"
              >
                <div className={`w-12 h-12 bg-gradient-to-r ${feature.color} rounded-lg flex items-center justify-center mb-4`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                
                <p className="text-gray-600 text-sm">
                  {feature.description}
                </p>
              </motion.div>
            )
          })}
        </div>
      </motion.div>

      {/* How It Works Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="mb-16"
      >
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          {t('about.how.it.works')}
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step, index) => {
            const Icon = step.icon
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 + index * 0.1 }}
                className="relative"
              >
                {index < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-6 left-full w-full">
                    <ArrowRight className="w-6 h-6 text-gray-300" />
                  </div>
                )}
                
                <div className="bg-white rounded-lg shadow-lg p-6 h-full">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                    <Icon className="w-6 h-6 text-blue-600" />
                  </div>
                  
                  <div className="flex items-center mb-2">
                    <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-semibold mr-3">
                      {index + 1}
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {step.title}
                    </h3>
                  </div>
                  
                  <p className="text-gray-600 text-sm">
                    {step.description}
                  </p>
                </div>
              </motion.div>
            )
          })}
        </div>
      </motion.div>

      {/* Technology Stack Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="mb-16"
      >
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white">
          <h2 className="text-3xl font-bold text-center mb-8">
            Technology Stack
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <h3 className="text-xl font-semibold mb-4">Frontend</h3>
              <ul className="space-y-2 text-blue-100">
                <li>React.js</li>
                <li>TypeScript</li>
                <li>Tailwind CSS</li>
                <li>Framer Motion</li>
              </ul>
            </div>
            
            <div className="text-center">
              <h3 className="text-xl font-semibold mb-4">Backend</h3>
              <ul className="space-y-2 text-blue-100">
                <li>FastAPI</li>
                <li>Python</li>
                <li>PyTorch</li>
                <li>OpenCV</li>
              </ul>
            </div>
            
            <div className="text-center">
              <h3 className="text-xl font-semibold mb-4">AI/ML</h3>
              <ul className="space-y-2 text-blue-100">
                <li>ResNet50</li>
                <li>EfficientNet</li>
                <li>Grad-CAM</li>
                <li>Transfer Learning</li>
              </ul>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Disclaimer Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
        className="bg-yellow-50 border border-yellow-200 rounded-lg p-8"
      >
        <div className="flex items-start space-x-3">
          <CheckCircle className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-lg font-semibold text-yellow-900 mb-2">
              Important Disclaimer
            </h3>
            <p className="text-yellow-800">
              {t('home.disclaimer')} This system is designed for educational and research purposes only. 
              The predictions provided by this AI should not be used as a substitute for professional medical 
              advice, diagnosis, or treatment. Always seek the advice of qualified healthcare providers with 
              any questions you may have regarding a medical condition.
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default About
