#!/usr/bin/env python3
"""
Image Recognition Module for Medical Analysis
Analyzes uploaded images to identify medical conditions and provide recommendations
"""

import base64
import io
import logging
import requests
import json
from typing import Dict, List, Optional, Tuple
from PIL import Image
import os
from config import Config

logger = logging.getLogger(__name__)

class MedicalImageAnalyzer:
    """Analyzes medical images using AI vision models"""
    
    def __init__(self):
        """Initialize the image analyzer"""
        self.claude_api_key = Config.CLAUDE_API_KEY
        self.claude_url = "https://api.anthropic.com/v1/messages"
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
        self.max_image_size = 10 * 1024 * 1024  # 10MB
        
    def analyze_medical_image(self, image_data: bytes, user_description: str = "") -> Dict:
        """
        Analyze a medical image and provide diagnosis/recommendations
        
        Args:
            image_data: Raw image bytes
            user_description: User's description of the image/symptoms
            
        Returns:
            Analysis results with diagnosis and recommendations
        """
        try:
            # Validate image
            validation_result = self._validate_image(image_data)
            if not validation_result['valid']:
                return validation_result
            
            # Convert image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Analyze with Claude Vision
            analysis_result = self._analyze_with_claude_vision(image_base64, user_description)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Error analyzing medical image: {str(e)}")
            return {
                'success': False,
                'error': f"Failed to analyze image: {str(e)}",
                'recommendations': ['Please try uploading a clearer image', 'Consult a healthcare professional for accurate diagnosis']
            }
    
    def _validate_image(self, image_data: bytes) -> Dict:
        """Validate uploaded image"""
        try:
            # Check file size
            if len(image_data) > self.max_image_size:
                return {
                    'valid': False,
                    'error': 'Image file is too large. Please upload an image smaller than 10MB.',
                    'success': False
                }
            
            # Check if it's a valid image
            try:
                image = Image.open(io.BytesIO(image_data))
                image.verify()
            except Exception:
                return {
                    'valid': False,
                    'error': 'Invalid image format. Please upload a valid image file.',
                    'success': False
                }
            
            # Check image dimensions
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size
            
            if width < 100 or height < 100:
                return {
                    'valid': False,
                    'error': 'Image resolution is too low. Please upload a higher quality image.',
                    'success': False
                }
            
            return {'valid': True, 'success': True}
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Error validating image: {str(e)}',
                'success': False
            }
    
    def _analyze_with_claude_vision(self, image_base64: str, user_description: str) -> Dict:
        """Analyze image using Claude Vision API"""
        try:
            if not self.claude_api_key:
                return {
                    'success': False,
                    'error': 'Claude API key not available for image analysis',
                    'recommendations': ['Please use text-based symptom analysis instead']
                }
            
            headers = {
                "x-api-key": self.claude_api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            
            # Create comprehensive medical image analysis prompt
            system_prompt = """You are a highly skilled medical AI assistant with expertise in analyzing medical images. Your role is to:

1. **Analyze the uploaded medical image carefully**
2. **Address the user's specific questions and concerns**
3. **Identify potential medical conditions or abnormalities**
4. **Provide evidence-based medical insights**
5. **Suggest appropriate next steps and recommendations**
6. **Always prioritize patient safety**

IMPORTANT GUIDELINES:
- Be thorough but cautious in your analysis
- Consider multiple possible diagnoses
- Provide confidence levels for your assessments
- Suggest when immediate medical attention is needed
- Include relevant medical terminology
- Recommend appropriate diagnostic tests if needed
- Suggest potential treatments or medications
- Always advise consulting healthcare professionals
- **Directly address the user's specific questions and concerns**

RESPONSE FORMAT (JSON only):
{
    "analysis_method": "Claude Vision Medical Analysis",
    "user_query_addressed": "Brief summary of how you addressed their specific question",
    "image_analysis": {
        "visual_findings": ["finding1", "finding2"],
        "potential_conditions": [
            {
                "condition": "condition_name",
                "confidence": 85,
                "severity": "low|moderate|high|critical",
                "description": "detailed_description",
                "differential_diagnosis": ["alternative1", "alternative2"]
            }
        ],
        "recommended_tests": ["test1", "test2"],
        "immediate_actions": ["action1", "action2"],
        "when_to_seek_help": "specific guidance"
    },
    "medicine_recommendations": {
        "otc_medicines": [
            {
                "name": "medicine_name",
                "purpose": "what it treats",
                "dosage": "recommended_dosage",
                "warnings": ["warning1", "warning2"]
            }
        ],
        "prescription_medicines": [],
        "natural_remedies": [],
        "contraindications": ["contraindication1", "contraindication2"]
    },
    "safety_alerts": ["alert1", "alert2"],
    "recommendations": ["recommendation1", "recommendation2"],
    "warnings": ["warning1", "warning2"]
}

Remember: Respond ONLY with valid JSON, no additional text."""

            # Create user prompt that incorporates their specific query
            if user_description.strip():
                user_prompt = f"""Please analyze this medical image and provide a comprehensive medical assessment that directly addresses the user's specific question.

USER'S QUESTION/CONCERN: {user_description}

Please provide your analysis in the exact JSON format specified above. Focus on:
- Directly answering the user's specific question
- Visual findings in the image
- Most likely medical conditions
- Appropriate confidence levels
- Safety-focused recommendations
- When to seek medical help
- Relevant medicine recommendations
- Addressing their specific concerns

Remember: Respond ONLY with valid JSON, no additional text."""
            else:
                user_prompt = f"""Please analyze this medical image and provide a comprehensive medical assessment.

No specific question provided - please provide general analysis.

Please provide your analysis in the exact JSON format specified above. Focus on:
- Visual findings in the image
- Most likely medical conditions
- Appropriate confidence levels
- Safety-focused recommendations
- When to seek medical help
- Relevant medicine recommendations

Remember: Respond ONLY with valid JSON, no additional text."""

            data = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 4000,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": user_prompt
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_base64
                                }
                            }
                        ]
                    }
                ],
                "system": system_prompt
            }
            
            logger.info("🔍 Sending medical image for Claude Vision analysis...")
            response = requests.post(self.claude_url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('content', [])
                
                if content and len(content) > 0:
                    analysis_text = content[0].get('text', '').strip()
                    logger.info("✅ Medical image analysis completed successfully")
                    
                    # Parse JSON response
                    try:
                        if '```json' in analysis_text:
                            json_start = analysis_text.find('```json') + 7
                            json_end = analysis_text.find('```', json_start)
                            json_content = analysis_text[json_start:json_end].strip()
                        else:
                            json_content = analysis_text.strip()
                        
                        parsed_analysis = json.loads(json_content)
                        parsed_analysis['success'] = True
                        parsed_analysis['raw_response'] = analysis_text
                        
                        logger.info(f"✅ Found {len(parsed_analysis.get('image_analysis', {}).get('potential_conditions', []))} potential conditions")
                        return parsed_analysis
                        
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse Claude Vision JSON response: {e}")
                        return {
                            'success': True,
                            'analysis_method': 'Claude Vision Analysis (Text Parsed)',
                            'user_query_addressed': 'Analysis provided but response format needs adjustment',
                            'raw_response': analysis_text,
                            'image_analysis': {
                                'visual_findings': ['Image analyzed successfully'],
                                'potential_conditions': [
                                    {
                                        'condition': 'Image Analysis Available',
                                        'confidence': 70,
                                        'severity': 'moderate',
                                        'description': 'Claude Vision provided analysis but response format needs adjustment',
                                        'immediate_actions': ['Review AI analysis', 'Consult healthcare provider'],
                                        'when_to_seek_help': 'If symptoms persist or worsen'
                                    }
                                ],
                                'recommended_tests': ['Consult healthcare professional'],
                                'immediate_actions': ['Review detailed analysis'],
                                'when_to_seek_help': 'Based on AI analysis'
                            },
                            'medicine_recommendations': {
                                'otc_medicines': [],
                                'prescription_medicines': [],
                                'natural_remedies': [],
                                'contraindications': []
                            },
                            'safety_alerts': ['This is AI-generated information'],
                            'recommendations': ['Review AI analysis', 'Consult healthcare professional'],
                            'warnings': ['Always consult healthcare professionals for accurate diagnosis']
                        }
                else:
                    logger.warning("Empty response from Claude Vision")
                    return {
                        'success': False,
                        'error': 'No analysis received from AI',
                        'recommendations': ['Please try uploading a different image', 'Consult healthcare professional']
                    }
            else:
                logger.error(f"Claude Vision API error: {response.status_code}")
                return {
                    'success': False,
                    'error': f'AI analysis failed: {response.status_code}',
                    'recommendations': ['Please try again later', 'Use text-based symptom analysis']
                }
                
        except Exception as e:
            logger.error(f"Error in Claude Vision analysis: {str(e)}")
            return {
                'success': False,
                'error': f'Analysis error: {str(e)}',
                'recommendations': ['Please try again', 'Consult healthcare professional']
            }
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported image formats"""
        return self.supported_formats
    
    def get_max_file_size(self) -> int:
        """Get maximum allowed file size in bytes"""
        return self.max_image_size

# Global instance
medical_image_analyzer = MedicalImageAnalyzer()
