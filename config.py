import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Debug: Print environment variables
print(f"🔧 Config loading - Claude API Key: {os.environ.get('CLAUDE_API_KEY', 'Not found')[:20] if os.environ.get('CLAUDE_API_KEY') else 'Not found'}")

class Config:
    """Basic configuration for the Medical Symptoms-to-Diagnosis Agent"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # AI API Keys - Load from environment variables
    TOGETHER_API_KEY = os.environ.get('TOGETHER_API_KEY')
    HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY')
    CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY')
    
    # Medical APIs
    FDA_API_KEY = os.environ.get('FDA_API_KEY')
    PUBMED_API_KEY = os.environ.get('PUBMED_API_KEY')
    
    # WHO GHO API (FREE & OPEN SOURCE - No API Key Required!)
    WHO_GHO_BASE_URL = "https://ghoapi.azureedge.net/api"
    
    # Application settings
    MAX_SYMPTOMS_LENGTH = 1000
    MAX_DIAGNOSES_RETURNED = 5
    
    # Medical disclaimer
    MEDICAL_DISCLAIMER = """
    This application is for educational purposes only and should not replace professional medical advice. 
    Always consult with a healthcare professional for proper diagnosis and treatment. 
    If you are experiencing severe symptoms, seek immediate medical attention.
    """
    
    # Common conditions for basic analysis
    COMMON_CONDITIONS = [
        'headache', 'fever', 'cough', 'fatigue', 'nausea', 'dizziness',
        'chest pain', 'shortness of breath', 'abdominal pain', 'back pain',
        'burn', 'hand burn', 'skin burn', 'pain', 'swelling', 'redness'
    ]
    
    # Medical sources
    MEDICAL_SOURCES = [
        'Local Medical Database',
        'Basic Symptom Analysis'
    ] 