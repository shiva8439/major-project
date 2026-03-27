from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import requests
import os
from ..models.prediction import ChatRequest, ChatResponse

router = APIRouter(prefix="/api", tags=["chatbot"])

# Medical knowledge base for basic responses
MEDICAL_KNOWLEDGE = {
    "en": {
        "greetings": [
            "Hello! I'm your medical AI assistant. How can I help you today?",
            "Hi! I'm here to provide basic medical information. What would you like to know?"
        ],
        "disclaimer": "I'm an AI assistant and not a substitute for professional medical advice. Please consult a healthcare provider for medical concerns.",
        "pneumonia": {
            "symptoms": "Common symptoms of pneumonia include cough, fever, chills, shortness of breath, and chest pain.",
            "causes": "Pneumonia is typically caused by bacteria, viruses, or fungi infecting the lungs.",
            "prevention": "Vaccination, good hygiene, and avoiding smoking can help prevent pneumonia."
        },
        "brain_tumor": {
            "symptoms": "Brain tumor symptoms may include headaches, seizures, vision problems, and difficulty with balance.",
            "types": "Brain tumors can be benign (non-cancerous) or malignant (cancerous).",
            "treatment": "Treatment options include surgery, radiation therapy, and chemotherapy."
        },
        "chest_xray": {
            "purpose": "Chest X-rays help visualize the heart, lungs, and bones in the chest.",
            "preparation": "No special preparation is needed for a chest X-ray.",
            "safety": "Chest X-rays use low levels of radiation and are generally safe."
        },
        "brain_mri": {
            "purpose": "Brain MRI uses magnetic fields to create detailed images of brain structures.",
            "preparation": "Remove metal objects and inform the doctor about any implants.",
            "safety": "MRI is non-invasive and doesn't use radiation."
        }
    },
    "hi": {
        "greetings": [
            "नमस्ते! मैं आपका मेडिकल AI सहायक हूँ। आज मैं आपकी कैसे मदद कर सकता हूँ?",
            "हैलो! मैं बुनियादी चिकित्सा जानकारी प्रदान करने के लिए यहाँ हूँ। आप क्या जानना चाहेंगे?"
        ],
        "disclaimer": "मैं एक AI सहायक हूँ और पेशेवर चिकित्सा सलाह का विकल्प नहीं हूँ। चिकित्सा चिंताओं के लिए कृपया हेल्थकेयर प्रदाता से परामर्श करें।",
        "pneumonia": {
            "symptoms": "निमोनिया के आम लक्षणों में खांसी, बुखार, ठंड लगना, सांस लेने में कठिनाई, और सीने में दर्द शामिल हैं।",
            "causes": "निमोनिया आमतौर पर बैक्टीरिया, वायरस, या कवक द्वारा फेफड़ों के संक्रमण के कारण होता है।",
            "prevention": "टीकाकरण, अच्छी स्वच्छता, और धूम्रपान से बचने से निमोनिया को रोकने में मदद मिल सकती है।"
        },
        "brain_tumor": {
            "symptoms": "ब्रेन ट्यूमर के लक्षणों में सिरदर्द, दौरे, दृष्टि समस्याएं, और संतुलन में कठिनाई शामिल हो सकते हैं।",
            "types": "ब्रेन ट्यूमर सौम्य (गैर-कैंसर) या घातक (कैंसर) हो सकते हैं।",
            "treatment": "उपचार विकल्पों में सर्जरी, रेडिएशन थेरेपी, और कीमोथेरेपी शामिल हैं।"
        },
        "chest_xray": {
            "purpose": "छाती का X-रे हृदय, फेफड़ों, और छाती की हड्डियों को देखने में मदद करता है।",
            "preparation": "छाती के X-रे के लिए कोई विशेष तैयारी की आवश्यकता नहीं है।",
            "safety": "छाती के X-रे कम स्तर के विकिरण का उपयोग करते हैं और आमतौर पर सुरक्षित होते हैं।"
        },
        "brain_mri": {
            "purpose": "ब्रेन MRI चुंबकीय क्षेत्रों का उपयोग करके ब्रेन संरचनाओं के विस्तृत चित्र बनाता है।",
            "preparation": "धातु की वस्तुओं को हटा दें और किसी भी इम्प्लांट के बारे में डॉक्टर को सूचित करें।",
            "safety": "MRI गैर-इनवेसिव है और विकिरण का उपयोग नहीं करता है।"
        }
    }
}

@router.post("/chat", response_model=ChatResponse)
async def chat_with_medical_bot(request: ChatRequest):
    """
    Chat with medical AI assistant
    
    Args:
        request: Chat request with message and language preference
        
    Returns:
        Chat response with medical information
    """
    try:
        language = request.language.lower()
        if language not in ["en", "hi"]:
            language = "en"
        
        message = request.message.lower().strip()
        
        # Check for greetings
        if any(greeting in message for greeting in ["hello", "hi", "नमस्ते", "हैलो"]):
            return ChatResponse(
                response=MEDICAL_KNOWLEDGE[language]["greetings"][0]
            )
        
        # Check for specific medical topics
        if "pneumonia" in message or "निमोनिया" in message:
            if "symptom" in message or "लक्षण" in message:
                return ChatResponse(
                    response=MEDICAL_KNOWLEDGE[language]["pneumonia"]["symptoms"]
                )
            elif "cause" in message or "कारण" in message:
                return ChatResponse(
                    response=MEDICAL_KNOWLEDGE[language]["pneumonia"]["causes"]
                )
            elif "prevent" in message or "रोकथाम" in message:
                return ChatResponse(
                    response=MEDICAL_KNOWLEDGE[language]["pneumonia"]["prevention"]
                )
            else:
                return ChatResponse(
                    response=f"{MEDICAL_KNOWLEDGE[language]['pneumonia']['symptoms']} {MEDICAL_KNOWLEDGE[language]['disclaimer']}"
                )
        
        if "brain tumor" in message or "brain tumour" in message or "ब्रेन ट्यूमर" in message:
            if "symptom" in message or "लक्षण" in message:
                return ChatResponse(
                    response=MEDICAL_KNOWLEDGE[language]["brain_tumor"]["symptoms"]
                )
            elif "type" in message or "प्रकार" in message:
                return ChatResponse(
                    response=MEDICAL_KNOWLEDGE[language]["brain_tumor"]["types"]
                )
            elif "treat" in message or "उपचार" in message:
                return ChatResponse(
                    response=MEDICAL_KNOWLEDGE[language]["brain_tumor"]["treatment"]
                )
            else:
                return ChatResponse(
                    response=f"{MEDICAL_KNOWLEDGE[language]['brain_tumor']['symptoms']} {MEDICAL_KNOWLEDGE[language]['disclaimer']}"
                )
        
        if "chest xray" in message or "chest x-ray" in message or "छाती x-रे" in message:
            if "purpose" in message or "उद्देश्य" in message:
                return ChatResponse(
                    response=MEDICAL_KNOWLEDGE[language]["chest_xray"]["purpose"]
                )
            elif "prepare" in message or "तैयारी" in message:
                return ChatResponse(
                    response=MEDICAL_KNOWLEDGE[language]["chest_xray"]["preparation"]
                )
            else:
                return ChatResponse(
                    response=f"{MEDICAL_KNOWLEDGE[language]['chest_xray']['purpose']} {MEDICAL_KNOWLEDGE[language]['disclaimer']}"
                )
        
        if "brain mri" in message or "ब्रेन mri" in message:
            if "purpose" in message or "उद्देश्य" in message:
                return ChatResponse(
                    response=MEDICAL_KNOWLEDGE[language]["brain_mri"]["purpose"]
                )
            elif "prepare" in message or "तैयारी" in message:
                return ChatResponse(
                    response=MEDICAL_KNOWLEDGE[language]["brain_mri"]["preparation"]
                )
            else:
                return ChatResponse(
                    response=f"{MEDICAL_KNOWLEDGE[language]['brain_mri']['purpose']} {MEDICAL_KNOWLEDGE[language]['disclaimer']}"
                )
        
        # Default response
        if language == "hi":
            return ChatResponse(
                response="मैं निमोनिया, ब्रेन ट्यूमर, छाती X-रे, और ब्रेन MRI के बारे में जानकारी प्रदान कर सकता हूँ। कृपया विशिष्ट प्रश्न पूछें। " + MEDICAL_KNOWLEDGE[language]["disclaimer"]
            )
        else:
            return ChatResponse(
                response="I can provide information about pneumonia, brain tumors, chest X-rays, and brain MRIs. Please ask specific questions. " + MEDICAL_KNOWLEDGE[language]["disclaimer"]
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
