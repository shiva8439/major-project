import React, { createContext, useContext, useState, ReactNode } from 'react'

type Language = 'en' | 'hi'

interface LanguageContextType {
  language: Language
  setLanguage: (lang: Language) => void
  t: (key: string) => string
}

const translations = {
  en: {
    // Navigation
    'nav.home': 'Home',
    'nav.about': 'About',
    'nav.history': 'History',
    'nav.language': 'Language',
    
    // Home Page
    'home.title': 'AI Medical Diagnosis System',
    'home.subtitle': 'Analyze medical images with advanced AI technology',
    'home.upload.title': 'Upload Medical Image',
    'home.upload.subtitle': 'Drag and drop or click to upload',
    'home.select.type': 'Select Image Type',
    'home.type.chest': 'Chest X-ray',
    'home.type.brain': 'Brain MRI',
    'home.analyze': 'Analyze Image',
    'home.analyzing': 'Analyzing...',
    'home.results.title': 'Analysis Results',
    'home.prediction': 'Prediction',
    'home.confidence': 'Confidence',
    'home.processing.time': 'Processing Time',
    'home.heatmap.title': 'Grad-CAM Heatmap',
    'home.heatmap.subtitle': 'Visualization of affected areas',
    'home.disclaimer': 'This is not a medical diagnosis tool. Always consult a healthcare professional.',
    
    // Chatbot
    'chat.title': 'Medical Assistant',
    'chat.placeholder': 'Ask about medical conditions...',
    'chat.send': 'Send',
    'chat.typing': 'Typing...',
    
    // History
    'history.title': 'Prediction History',
    'history.no.data': 'No previous predictions found',
    'history.date': 'Date',
    'history.type': 'Type',
    'history.result': 'Result',
    'history.confidence': 'Confidence',
    
    // About Page
    'about.title': 'About',
    'about.subtitle': 'Learn about our AI-powered medical diagnosis system',
    'about.features.title': 'Features',
    'about.feature.ai': 'AI-Powered Analysis',
    'about.feature.ai.desc': 'Advanced deep learning models for accurate medical image analysis',
    'about.feature.explainable': 'Explainable AI',
    'about.feature.explainable.desc': 'Grad-CAM visualizations show what the AI is looking at',
    'about.feature.multilingual': 'Multilingual Support',
    'about.feature.multilingual.desc': 'Available in English and Hindi for broader accessibility',
    'about.feature.chatbot': 'AI Chatbot',
    'about.feature.chatbot.desc': 'Get answers to your medical questions from our AI assistant',
    'about.how.it.works': 'How It Works',
    'about.step1': 'Upload your medical image',
    'about.step2': 'AI analyzes the image using deep learning',
    'about.step3': 'Get prediction with confidence score',
    'about.step4': 'View Grad-CAM heatmap for explanation',
    
    // Common
    'common.loading': 'Loading...',
    'common.error': 'Error',
    'common.success': 'Success',
    'common.retry': 'Retry',
    'common.close': 'Close',
    'common.save': 'Save',
    'common.download': 'Download',
    'common.share': 'Share',
    'common.clear': 'Clear',
    'common.cancel': 'Cancel',
    'common.confirm': 'Confirm',
    'common.yes': 'Yes',
    'common.no': 'No',
    
    // Messages
    'msg.upload.success': 'Image uploaded successfully',
    'msg.upload.image': 'Please upload a valid image file',
    'msg.analysis.success': 'Analysis completed successfully',
    'msg.file.too.large': 'File size exceeds 10MB limit',
    'msg.invalid.file': 'Please upload a valid image file',
    'msg.server.error': 'Server error. Please try again later.',
    'msg.analysis.error': 'Analysis failed. Please try again.',
  },
  hi: {
    // Navigation
    'nav.home': 'होम',
    'nav.about': 'के बारे में',
    'nav.history': 'इतिहास',
    'nav.language': 'भाषा',
    
    // Home Page
    'home.title': 'AI मेडिकल डायग्नोसिस सिस्टम',
    'home.subtitle': 'उन्नत AI तकनीक के साथ मेडिकल इमेज का विश्लेषण करें',
    'home.upload.title': 'मेडिकल इमेज अपलोड करें',
    'home.upload.subtitle': 'ड्रैग और ड्रॉप करें या अपलोड करने के लिए क्लिक करें',
    'home.select.type': 'इमेज प्रकार चुनें',
    'home.type.chest': 'छाती X-रे',
    'home.type.brain': 'ब्रेन MRI',
    'home.analyze': 'इमेज का विश्लेषण करें',
    'home.analyzing': 'विश्लेषण कर रहे हैं...',
    'home.results.title': 'विश्लेषण परिणाम',
    'home.prediction': 'भविष्यवाणी',
    'home.confidence': 'आत्मविश्वास',
    'home.processing.time': 'प्रसंस्करण समय',
    'home.heatmap.title': 'Grad-CAM हीटमैप',
    'home.heatmap.subtitle': 'प्रभावित क्षेत्रों का विज़ुअलाइज़ेशन',
    'home.disclaimer': 'यह एक मेडिकल डायग्नोसिस टूल नहीं है। हमेशा एक हेल्थकेयर पेशेवर से परामर्श करें।',
    
    // Chatbot
    'chat.title': 'मेडिकल सहायक',
    'chat.placeholder': 'मेडिकल स्थितियों के बारे में पूछें...',
    'chat.send': 'भेजें',
    'chat.typing': 'टाइप कर रहे हैं...',
    
    // History
    'history.title': 'भविष्यवाणी इतिहास',
    'history.no.data': 'कोई पिछली भविष्यवाणी नहीं मिली',
    'history.date': 'दिनांक',
    'history.type': 'प्रकार',
    'history.result': 'परिणाम',
    'history.confidence': 'आत्मविश्वास',
    
    // About Page
    'about.title': 'के बारे में',
    'about.subtitle': 'हमारे AI-संचालित मेडिकल डायग्नोसिस सिस्टम के बारे में जानें',
    'about.features.title': 'विशेषताएं',
    'about.feature.ai': 'AI-संचालित विश्लेषण',
    'about.feature.ai.desc': 'सटीक मेडिकल इमेज विश्लेषण के लिए उन्नत डीप लर्निंग मॉडल',
    'about.feature.explainable': 'स्पष्ट AI',
    'about.feature.explainable.desc': 'Grad-CAM विज़ुअलाइज़ेशन दिखाते हैं कि AI क्या देख रहा है',
    'about.feature.multilingual': 'बहुभाषी समर्थन',
    'about.feature.multilingual.desc': 'व्यापक पहुंच के लिए अंग्रेजी और हिंदी में उपलब्ध',
    'about.feature.chatbot': 'AI चैटबॉट',
    'about.feature.chatbot.desc': 'हमारे AI सहायक से अपने मेडिकल प्रश्नों के उत्तर प्राप्त करें',
    'about.how.it.works': 'यह कैसे काम करता है',
    'about.step1': 'अपनी मेडिकल इमेज अपलोड करें',
    'about.step2': 'AI डीप लर्निंग का उपयोग करके इमेज का विश्लेषण करता है',
    'about.step3': 'आत्मविश्वास स्कोर के साथ भविष्यवाणी प्राप्त करें',
    'about.step4': 'स्पष्टीकरण के लिए Grad-CAM हीटमैप देखें',
    
    // Common
    'common.loading': 'लोड हो रहा है...',
    'common.error': 'त्रुटि',
    'common.success': 'सफलता',
    'common.retry': 'पुनः प्रयास करें',
    'common.close': 'बंद करें',
    'common.save': 'सहेजें',
    'common.download': 'डाउनलोड करें',
    'common.share': 'साझा करें',
    'common.clear': 'साफ करें',
    'common.cancel': 'रद्द करें',
    'common.confirm': 'पुष्टि करें',
    'common.yes': 'हां',
    'common.no': 'नहीं',
    
    // Messages
    'msg.upload.success': 'इमेज सफलतापूर्वक अपलोड हुई',
    'msg.upload.error': 'इमेज अपलोड करने में विफल',
    'msg.analysis.success': 'विश्लेषण सफलतापूर्वक पूरा हुआ',
    'msg.analysis.error': 'विश्लेषण विफल',
    'msg.network.error': 'नेटवर्क त्रुटि। कृपया अपना कनेक्शन जांचें।',
    'msg.file.too.large': 'फाइल साइज 10MB सीमा से अधिक है',
    'msg.invalid.file': 'कृपया एक वैध इमेज फाइल अपलोड करें',
    'msg.server.error': 'सर्वर त्रुटि। कृपया बाद में पुनः प्रयास करें।',
  }
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined)

export const useLanguage = () => {
  const context = useContext(LanguageContext)
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider')
  }
  return context
}

interface LanguageProviderProps {
  children: ReactNode
}

export const LanguageProvider: React.FC<LanguageProviderProps> = ({ children }) => {
  const [language, setLanguage] = useState<Language>('en')

  const t = (key: string): string => {
    return translations[language][key as keyof typeof translations.en] || key
  }

  const value: LanguageContextType = {
    language,
    setLanguage,
    t
  }

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  )
}
