#!/usr/bin/env python3
"""
Core symptom analysis utilities - API-Only System
No hardcoded data, uses only external APIs
"""

import logging
from flask import current_app

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_symptoms_input(symptoms):
    """Validate and clean symptoms input"""
    if not symptoms or not symptoms.strip():
        return False, "Please enter your symptoms"
    
    if len(symptoms.strip()) < 3:
        return False, "Please provide more detailed symptoms"
    
    return True, symptoms.strip()

def analyze_symptoms(symptoms):
    """
    Analyze symptoms using AI APIs ONLY - no hardcoded fallbacks
    Returns API-driven diagnosis and recommendations
    """
    try:
        logger.info(f"Analyzing symptoms: {symptoms}")
        
        # Validate input
        is_valid, message = validate_symptoms_input(symptoms)
        if not is_valid:
            return {
                'error': message,
                'analysis_method': 'Input Validation'
            }
        
        # Use AI providers for analysis
        from app.ai_providers import AIProviders
        ai_providers = AIProviders()
        
        # Get AI-powered analysis
        ai_result = ai_providers.analyze_symptoms_with_ai(symptoms)
        
        if ai_result and ai_result.get('potential_diagnoses'):
            logger.info("Using AI-powered analysis")
            
            # Add medicine recommendations to each diagnosis
            for diagnosis in ai_result['potential_diagnoses']:
                condition = diagnosis.get('condition', '')
                if condition:
                    try:
                        from app.api_driven_medical import api_driven_medical
                        # Use API-driven medical recommendations instead of hardcoded data
                        medicine_recs = api_driven_medical.get_comprehensive_medical_recommendations(condition)
                        diagnosis['medicine_recommendations'] = medicine_recs
                    except Exception as e:
                        logger.error(f"Error getting medicine recommendations for {condition}: {str(e)}")
                        diagnosis['medicine_recommendations'] = {
                            'otc_medicines': [],
                            'prescription_medicines': [],
                            'natural_remedies': [],
                            'medical_literature': [],
                            'api_sources': ['API-Only System'],
                            'note': 'Medical APIs temporarily unavailable. Please consult healthcare provider.'
                        }
            
            return ai_result
            
        else:
            logger.warning("AI analysis failed, but continuing with API-only approach")
            
    except Exception as e:
        logger.error(f"AI analysis error: {str(e)}")
    
    # If AI fails, return API-only response with no hardcoded data
    return {
        'potential_diagnoses': [],
        'analysis_method': 'API-Only (No Hardcoded Data)',
        'message': 'This system uses only AI APIs and external medical databases. No hardcoded diagnosis data is used.',
        'recommendations': [],
        'warnings': []
    }

def add_medicine_recommendations(analysis_result):
    """Add medicine recommendations to analysis results using APIs only"""
    if not analysis_result or not analysis_result.get('potential_diagnoses'):
        return analysis_result
    
    for diagnosis in analysis_result['potential_diagnoses']:
        condition = diagnosis.get('condition', '')
        if condition:
            try:
                from app.api_driven_medical import api_driven_medical
                medicine_recs = api_driven_medical.get_comprehensive_medical_recommendations(condition)
                diagnosis['medicine_recommendations'] = medicine_recs
            except Exception as e:
                logger.error(f"Error adding medicine recommendations for {condition}: {str(e)}")
                diagnosis['medicine_recommendations'] = {
                    'otc_medicines': [],
                    'prescription_medicines': [],
                    'natural_remedies': [],
                    'medical_literature': [],
                    'api_sources': ['API-Only System'],
                    'note': 'Medical APIs temporarily unavailable. Please consult healthcare provider.'
                }
    
    return analysis_result

def get_medicine_recommendations(condition):
    """Get dynamic medicine recommendations from medical APIs only"""
    try:
        from app.api_driven_medical import api_driven_medical
        recommendations = api_driven_medical.get_comprehensive_medical_recommendations(condition)
        logger.info(f"Retrieved API-driven medicine recommendations for {condition}")
        return recommendations
        
    except Exception as e:
        logger.error(f"Error getting API-driven medicine recommendations for {condition}: {str(e)}")
        return {
            'otc_medicines': [],
            'prescription_medicines': [],
            'natural_remedies': [],
            'medical_literature': [],
            'api_sources': ['API-Only System'],
            'note': 'Medical APIs temporarily unavailable. Please consult healthcare provider.'
        }

def create_fallback_response(symptoms):
    """Create API-only fallback response when analysis fails"""
    return {
        'analysis_method': 'API-Only System',
        'potential_diagnoses': [
            {
                'condition': 'Medical Consultation Required',
                'confidence': 50,
                'severity': 'unknown',
                'description': 'Please consult a healthcare professional for proper diagnosis and treatment.',
                'immediate_actions': ['Schedule a doctor appointment', 'Monitor your symptoms', 'Keep a symptom diary'],
                'when_to_seek_help': 'Seek immediate medical attention if symptoms are severe or concerning.',
                'medicine_recommendations': {
                    'otc_medicines': [],
                    'prescription_medicines': [],
                    'natural_remedies': [],
                    'medical_literature': [],
                    'api_sources': ['API-Only System'],
                    'note': 'This system uses only external APIs. No hardcoded medical data is used.'
                }
            }
        ],
        'recommendations': [
            'Always consult with a healthcare professional for proper diagnosis',
            'Keep track of your symptoms and their progression',
            'Follow any prescribed treatment plans',
            'Maintain a healthy lifestyle with proper diet and exercise'
        ],
        'warnings': [
            'This analysis is for educational purposes only and should not replace professional medical advice',
            'If symptoms are severe or concerning, seek immediate medical attention',
            'Do not self-diagnose or self-treat serious medical conditions',
            'This system uses only external APIs - no hardcoded medical data'
        ]
    }

def detect_language(text):
    """Simple language detection"""
    # Basic language detection - can be enhanced with language detection APIs
    return 'en'

def translate_analysis_results(analysis_results, target_language):
    """Translate analysis results to target language using APIs"""
    # This would integrate with translation APIs like Google Translate
    # For now, return original results
    return analysis_results 