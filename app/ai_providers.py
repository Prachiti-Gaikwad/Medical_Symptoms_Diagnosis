#!/usr/bin/env python3
"""
AI Providers Module - Where API keys are connected for intelligent analysis
"""

import os
import requests
import json
import logging
from typing import Dict, List, Optional
from config import Config

logger = logging.getLogger(__name__)

class AIProviders:
    """AI providers for intelligent symptom analysis"""
    
    def __init__(self):
        # Get API Keys from config
        self.huggingface_api_key = Config.HUGGINGFACE_API_KEY
        self.together_api_key = Config.TOGETHER_API_KEY
        self.claude_api_key = Config.CLAUDE_API_KEY
        
        # Base URLs
        self.huggingface_url = "https://api-inference.huggingface.co/models"
        self.together_url = "https://api.together.xyz/v1"
        self.claude_url = "https://api.anthropic.com/v1/messages"
        
        # Models
        self.huggingface_model = "microsoft/DialoGPT-medium"
        self.together_model = "meta-llama/Llama-2-7b-chat-hf"
        self.claude_model = "claude-3-5-sonnet-20241022"  # Latest Claude model
        
        # Log API key status
        logger.info(f"Claude AI API Key: {'✅ Available' if self.claude_api_key else '❌ Not available'}")
        logger.info(f"Together AI API Key: {'✅ Available' if self.together_api_key else '❌ Not available'}")
        logger.info(f"Hugging Face API Key: {'✅ Available' if self.huggingface_api_key else '❌ Not available'}")
    
    def analyze_symptoms_with_ai(self, symptoms: str) -> Dict:
        """Analyze symptoms using AI APIs - prioritize Claude AI"""
        try:
            # 1. Try Claude AI first (most reliable)
            if self.claude_api_key:
                logger.info("Attempting Claude AI analysis...")
                claude_result = self._analyze_with_claude(symptoms)
                if claude_result and claude_result.get('potential_diagnoses'):
                    logger.info("Claude AI analysis successful")
                    return claude_result
            
            # 2. Try Together AI as backup
            if self.together_api_key:
                logger.info("Attempting Together AI analysis...")
                together_result = self._analyze_with_together_ai(symptoms)
                if together_result and together_result.get('potential_diagnoses'):
                    logger.info("Together AI analysis successful")
                    return together_result
            
            # 3. Try Hugging Face as last resort
            if self.huggingface_api_key:
                logger.info("Attempting Hugging Face analysis...")
                hf_result = self._analyze_with_huggingface(symptoms)
                if hf_result and hf_result.get('potential_diagnoses'):
                    logger.info("Hugging Face analysis successful")
                    return hf_result
            
            logger.warning("No AI providers available or all failed")
            return None
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            return None
    
    def _analyze_with_claude(self, symptoms: str) -> Dict:
        """Analyze symptoms using Claude AI"""
        headers = {
            "x-api-key": self.claude_api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        # Create a comprehensive medical prompt for Claude with user-friendly symptom interpretation
        system_prompt = """You are a helpful medical AI assistant. I will describe my symptoms in my own words. My input may contain spelling mistakes, grammar errors, or incorrect medical terms. Please analyze it carefully.

Your task is to:

1. **Identify and correct any misspelled or medically incorrect symptoms.**
2. **Interpret my message even if the grammar is wrong or informal.**
3. **Show the corrected and understood symptoms clearly.**
4. **If any symptom is unclear or not found, suggest similar or related known symptoms.**
5. **Proceed with giving a likely diagnosis or advice based on the corrected symptoms.**

For example:
- Original Input: "I'm feling dizzzy and hevvy hed with stomack ack"
- Corrected Symptoms: "feeling dizzy, heavy head, stomach ache"

You are a highly skilled medical AI assistant with expertise in symptom analysis and diagnosis. Your role is to:

1. Analyze patient symptoms carefully (with spelling correction)
2. Provide potential diagnoses with confidence levels
3. Suggest appropriate immediate actions
4. Recommend when to seek medical help
5. Always prioritize patient safety

IMPORTANT: You must respond ONLY in valid JSON format. Do not include any text outside the JSON structure.

Medical Guidelines:
- Always consider the most serious conditions first
- Provide evidence-based recommendations
- Include confidence levels (0-100%)
- Suggest immediate actions for safety
- Recommend medical consultation when appropriate
- Consider patient demographics and context
- Correct spelling mistakes and interpret informal language

Response Format (JSON only):
{
    "analysis_method": "Claude AI Medical Analysis",
    "corrected_symptoms": "corrected and understood symptoms",
    "symptom_corrections": {
        "original": "original input",
        "corrected": "corrected symptoms",
        "interpretations": ["interpretation1", "interpretation2"]
    },
    "potential_diagnoses": [
        {
            "condition": "diagnosis_name",
            "confidence": 85,
            "severity": "low|moderate|high|critical",
            "description": "detailed_description",
            "immediate_actions": ["action1", "action2", "action3"],
            "when_to_seek_help": "specific guidance on when to see a doctor"
        }
    ],
    "recommendations": ["general_recommendation1", "general_recommendation2"],
    "warnings": ["warning1", "warning2"]
}"""

        user_prompt = f"""Please analyze these symptoms and provide a medical assessment:

Original Symptoms: {symptoms}

IMPORTANT: First correct any spelling mistakes, grammar errors, or informal language in the symptoms. Then provide your analysis.

For example:
- If user says "I'm feling dizzzy and hevvy hed with stomack ack"
- Correct to: "feeling dizzy, heavy head, stomach ache"
- Then analyze the corrected symptoms

Provide your analysis in the exact JSON format specified above. Focus on:
- Correcting spelling mistakes and interpreting informal language
- Most likely diagnoses based on the corrected symptoms
- Appropriate confidence levels
- Safety-focused immediate actions
- Clear guidance on when to seek medical help

Remember: Respond ONLY with valid JSON, no additional text."""

        data = {
            "model": self.claude_model,
            "max_tokens": 4000,
            "messages": [
                {"role": "user", "content": user_prompt}
            ],
            "system": system_prompt,
            "temperature": 0.1  # Low temperature for consistent medical responses
        }
        
        logger.info(f"Sending request to Claude AI with model: {data['model']}")
        response = requests.post(self.claude_url, headers=headers, json=data, timeout=60)
        
        if response.status_code != 200:
            error_msg = f"Claude AI API error: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        result = response.json()
        logger.info("Claude AI analysis completed successfully")
        return self._parse_claude_response(result)
    
    def _analyze_with_together_ai(self, symptoms: str) -> Dict:
        """Analyze symptoms using Together AI"""
        url = f"{self.together_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.together_api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""
        Analyze these symptoms and provide a medical diagnosis in JSON format:
        Symptoms: {symptoms}
        
        Please provide a JSON response with this structure:
        {{
            "analysis_method": "Together AI Analysis",
            "potential_diagnoses": [
                {{
                    "condition": "diagnosis_name",
                    "confidence": 85,
                    "severity": "moderate",
                    "description": "description",
                    "immediate_actions": ["action1", "action2"],
                    "when_to_seek_help": "when to seek help"
                }}
            ]
        }}
        """
        
        data = {
            "model": "gpt2",
            "messages": [
                {"role": "system", "content": "You are a medical AI assistant. Provide accurate, helpful medical information in JSON format only."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2048,
            "temperature": 0.3
        }
        
        logger.info(f"Sending request to Together AI with model: {data['model']}")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code != 200:
            logger.error(f"Together AI API error: {response.status_code} - {response.text}")
            raise Exception(f"API Error: {response.status_code}")
        
        result = response.json()
        return self._parse_together_response(result)
    
    def _analyze_with_huggingface(self, symptoms: str) -> Dict:
        """Analyze symptoms using Hugging Face"""
        url = f"{self.huggingface_url}/{self.huggingface_model}"
        
        headers = {
            "Authorization": f"Bearer {self.huggingface_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "inputs": f"Analyze these symptoms: {symptoms}",
            "parameters": {
                "max_length": 500,
                "temperature": 0.7
            }
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return self._parse_huggingface_response(result)
    
    def _parse_claude_response(self, response: Dict) -> Dict:
        """Parse Claude AI response"""
        try:
            content = response['content'][0]['text']
            logger.info(f"Claude raw response: {content[:200]}...")
            
            # Try to parse JSON from the response
            try:
                # Extract JSON from the response (Claude might wrap it in markdown)
                if '```json' in content:
                    json_start = content.find('```json') + 7
                    json_end = content.find('```', json_start)
                    json_content = content[json_start:json_end].strip()
                else:
                    # Try to find JSON in the response
                    json_content = content.strip()
                
                parsed_response = json.loads(json_content)
                logger.info("Successfully parsed Claude JSON response")
                return parsed_response
                
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse Claude JSON response: {e}")
                # Fallback: create structured response from text
                return {
                    'analysis_method': 'Claude AI Analysis (Text Parsed)',
                    'raw_response': content,
                    'potential_diagnoses': [
                        {
                            'condition': 'AI Analysis Available',
                            'confidence': 70,
                            'severity': 'moderate',
                            'description': 'Claude AI provided analysis but response format needs adjustment',
                            'immediate_actions': ['Review AI response', 'Consult healthcare provider'],
                            'when_to_seek_help': 'If symptoms persist or worsen'
                        }
                    ],
                    'recommendations': ['AI analysis completed', 'Review detailed response'],
                    'warnings': ['This is AI-generated information', 'Always consult healthcare professionals']
                }
                
        except Exception as e:
            logger.error(f"Error parsing Claude response: {e}")
            return None
    
    def _parse_together_response(self, response: Dict) -> Dict:
        """Parse Together AI response"""
        try:
            content = response['choices'][0]['message']['content']
            # Parse JSON from content
            return json.loads(content)
        except Exception as e:
            logger.error(f"Error parsing Together AI response: {e}")
            return None
    
    def _parse_huggingface_response(self, response: Dict) -> Dict:
        """Parse Hugging Face response"""
        try:
            # Hugging Face returns generated text
            generated_text = response[0]['generated_text']
            # Convert to structured format
            return {
                'analysis_method': 'Hugging Face AI',
                'raw_response': generated_text,
                'needs_parsing': True
            }
        except Exception as e:
            logger.error(f"Error parsing Hugging Face response: {e}")
            return None
    
    def get_chatbot_response(self, prompt: str) -> str:
        """
        Get chatbot response using Claude AI
        
        Args:
            prompt: The prompt for the chatbot
            
        Returns:
            Chatbot response as string
        """
        try:
            if not self.claude_api_key:
                logger.warning("Claude API key not available for chatbot")
                return "I apologize, but I'm currently unable to provide medical advice. Please use the symptom analysis mode or consult a healthcare professional."
            
            headers = {
                "x-api-key": self.claude_api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.claude_model,
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            logger.info("Sending chatbot request to Claude AI...")
            response = requests.post(self.claude_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                content = response_data.get('content', [])
                
                if content and len(content) > 0:
                    chatbot_response = content[0].get('text', '').strip()
                    logger.info("Chatbot response received successfully")
                    return chatbot_response
                else:
                    logger.warning("Empty response from Claude AI")
                    return "I apologize, but I didn't receive a proper response. Please try again."
            
            else:
                logger.error(f"Claude AI chatbot request failed: {response.status_code}")
                return "I apologize, but I'm experiencing technical difficulties. Please try again or use the symptom analysis mode."
                
        except Exception as e:
            logger.error(f"Error in chatbot response: {str(e)}")
            return "I apologize, but I'm having trouble processing your request. Please try again or consult a healthcare professional."

# Global instance
ai_providers = AIProviders() 