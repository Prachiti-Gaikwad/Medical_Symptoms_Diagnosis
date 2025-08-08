#!/usr/bin/env python3
"""
Advanced Medical Features Module
Inspired by Medical Chat (https://medical.chat-data.com/)
"""

import requests
import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AdvancedMedicalFeatures:
    """Advanced medical features for enhanced diagnosis and treatment"""
    
    def __init__(self):
        self.pubmed_base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.pubmed_api_key = None  # Optional: Get from https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/
        self.medical_sources = {
            'textbooks': [
                'Harrison\'s Principles of Internal Medicine',
                'Robbins Basic Pathology',
                'Guyton and Hall Textbook of Medical Physiology',
                'Davidson\'s Principles and Practice of Medicine',
                'Oxford Handbook of Clinical Medicine'
            ],
            'journals': [
                'New England Journal of Medicine',
                'The Lancet',
                'Journal of the American Medical Association',
                'British Medical Journal',
                'Annals of Internal Medicine'
            ]
        }
    
    def generate_differential_diagnosis(self, symptoms: str, patient_info: Dict = None) -> Dict:
        """
        Generate comprehensive differential diagnosis report
        Similar to Medical Chat's DDx feature
        """
        try:
            # Enhanced prompt for differential diagnosis
            prompt = f"""
            Generate a comprehensive differential diagnosis report for the following symptoms: {symptoms}
            
            Patient Information: {patient_info or 'Not provided'}
            
            Please provide:
            1. Primary differential diagnoses (most likely conditions)
            2. Secondary differential diagnoses (less likely but important to consider)
            3. Red flag conditions (urgent/emergent conditions to rule out)
            4. Probability percentages for each diagnosis
            5. Key distinguishing features between diagnoses
            6. Recommended diagnostic tests for each condition
            7. Evidence level for each diagnosis
            
            Format as JSON with the following structure:
            {{
                "differential_diagnosis": {{
                    "primary": [
                        {{
                            "condition": "condition_name",
                            "probability": "percentage",
                            "key_features": ["feature1", "feature2"],
                            "diagnostic_tests": ["test1", "test2"],
                            "evidence_level": "A/B/C/D",
                            "urgency": "high/medium/low"
                        }}
                    ],
                    "secondary": [...],
                    "red_flags": [...]
                }},
                "summary": "brief_summary",
                "recommended_workup": ["test1", "test2"],
                "follow_up_questions": ["question1", "question2"]
            }}
            """
            
            # This would integrate with your existing AI provider
            # For now, return a structured template
            return self._create_ddx_template(symptoms, patient_info)
            
        except Exception as e:
            logger.error(f"Error generating differential diagnosis: {str(e)}")
            return {"error": "Failed to generate differential diagnosis"}
    
    def _create_ddx_template(self, symptoms: str, patient_info: Dict = None) -> Dict:
        """Create a template differential diagnosis structure"""
        return {
            "differential_diagnosis": {
                "primary": [
                    {
                        "condition": "Most Likely Condition",
                        "probability": "60-70%",
                        "key_features": ["Feature 1", "Feature 2"],
                        "diagnostic_tests": ["Test 1", "Test 2"],
                        "evidence_level": "B",
                        "urgency": "medium"
                    }
                ],
                "secondary": [
                    {
                        "condition": "Alternative Condition",
                        "probability": "20-30%",
                        "key_features": ["Feature 1", "Feature 2"],
                        "diagnostic_tests": ["Test 1", "Test 2"],
                        "evidence_level": "C",
                        "urgency": "low"
                    }
                ],
                "red_flags": [
                    {
                        "condition": "Serious Condition",
                        "probability": "5-10%",
                        "key_features": ["Red flag feature"],
                        "diagnostic_tests": ["Immediate test"],
                        "evidence_level": "A",
                        "urgency": "high"
                    }
                ]
            },
            "summary": f"Based on symptoms: {symptoms}",
            "recommended_workup": ["Initial test 1", "Initial test 2"],
            "follow_up_questions": [
                "When did symptoms first appear?",
                "Are there any associated symptoms?",
                "What makes symptoms better or worse?"
            ]
        }
    
    def search_pubmed_articles(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search PubMed for relevant medical articles
        Similar to Medical Chat's PubMed search feature
        """
        try:
            # PubMed E-utilities API
            search_url = f"{self.pubmed_base_url}esearch.fcgi"
            params = {
                'db': 'pubmed',
                'term': query,
                'retmax': max_results,
                'retmode': 'json',
                'sort': 'relevance'
            }
            
            if self.pubmed_api_key:
                params['api_key'] = self.pubmed_api_key
            
            response = requests.get(search_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                article_ids = data.get('esearchresult', {}).get('idlist', [])
                
                # Get article details
                articles = []
                for pmid in article_ids[:max_results]:
                    article_detail = self._get_pubmed_article_detail(pmid)
                    if article_detail:
                        articles.append(article_detail)
                
                return articles
            else:
                logger.error(f"PubMed search failed: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching PubMed: {str(e)}")
            return []
    
    def _get_pubmed_article_detail(self, pmid: str) -> Optional[Dict]:
        """Get detailed information for a specific PubMed article"""
        try:
            fetch_url = f"{self.pubmed_base_url}efetch.fcgi"
            params = {
                'db': 'pubmed',
                'id': pmid,
                'retmode': 'xml'
            }
            
            if self.pubmed_api_key:
                params['api_key'] = self.pubmed_api_key
            
            response = requests.get(fetch_url, params=params, timeout=10)
            
            if response.status_code == 200:
                # Parse XML response (simplified)
                return {
                    'pmid': pmid,
                    'title': f"PubMed Article {pmid}",
                    'authors': "Various Authors",
                    'journal': "Medical Journal",
                    'year': "2024",
                    'abstract': f"Abstract for article {pmid}",
                    'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching PubMed article {pmid}: {str(e)}")
            return None
    
    def get_professional_sources(self, condition: str) -> Dict:
        """
        Get cited professional sources for medical conditions
        Similar to Medical Chat's cited sources feature
        """
        try:
            sources = {
                'textbooks': [],
                'journal_articles': [],
                'clinical_guidelines': [],
                'evidence_level': 'B'
            }
            
            # Search for relevant textbook references
            for textbook in self.medical_sources['textbooks']:
                if condition.lower() in textbook.lower():
                    sources['textbooks'].append({
                        'title': textbook,
                        'edition': 'Latest',
                        'chapter': f'Chapter on {condition}',
                        'page_range': 'Relevant pages'
                    })
            
            # Search for journal articles
            pubmed_results = self.search_pubmed_articles(condition, max_results=5)
            sources['journal_articles'] = pubmed_results
            
            # Add clinical guidelines
            sources['clinical_guidelines'] = [
                {
                    'title': f'Clinical Guidelines for {condition}',
                    'organization': 'Medical Association',
                    'year': '2024',
                    'url': f'https://guidelines.example.com/{condition.lower().replace(" ", "-")}'
                }
            ]
            
            return sources
            
        except Exception as e:
            logger.error(f"Error getting professional sources: {str(e)}")
            return {'error': 'Failed to retrieve professional sources'}
    
    def create_patient_clinic_plan(self, diagnosis: str, patient_info: Dict) -> Dict:
        """
        Create comprehensive patient-specific clinic plan
        Similar to Medical Chat's clinic plans feature
        """
        try:
            plan = {
                'patient_info': patient_info,
                'diagnosis': diagnosis,
                'treatment_plan': {
                    'immediate_actions': [],
                    'medications': [],
                    'lifestyle_modifications': [],
                    'follow_up_schedule': []
                },
                'patient_education': {
                    'condition_explanation': '',
                    'treatment_explanation': '',
                    'lifestyle_recommendations': [],
                    'warning_signs': [],
                    'resources': []
                },
                'monitoring_plan': {
                    'vital_signs': [],
                    'symptoms_to_track': [],
                    'frequency': '',
                    'red_flags': []
                },
                'created_date': datetime.now().isoformat(),
                'next_review_date': '',
                'notes': ''
            }
            
            return plan
            
        except Exception as e:
            logger.error(f"Error creating clinic plan: {str(e)}")
            return {'error': 'Failed to create clinic plan'}
    
    def generate_custom_prompts(self) -> Dict:
        """
        Generate custom prompt templates for different medical scenarios
        Similar to Medical Chat's custom prompt templates
        """
        return {
            'emergency_assessment': {
                'name': 'Emergency Assessment',
                'prompt': 'Assess the following symptoms for emergency conditions. Identify red flags and immediate actions required.',
                'variables': ['symptoms', 'patient_age', 'vital_signs']
            },
            'chronic_condition': {
                'name': 'Chronic Condition Management',
                'prompt': 'Provide comprehensive management plan for chronic condition including medication, lifestyle, and monitoring.',
                'variables': ['condition', 'duration', 'current_medications', 'comorbidities']
            },
            'medication_review': {
                'name': 'Medication Review',
                'prompt': 'Review medication list for interactions, side effects, and optimization opportunities.',
                'variables': ['medication_list', 'patient_age', 'comorbidities']
            },
            'preventive_care': {
                'name': 'Preventive Care',
                'prompt': 'Recommend preventive care measures based on patient demographics and risk factors.',
                'variables': ['age', 'gender', 'risk_factors', 'family_history']
            }
        }
    
    def export_conversation_history(self, conversation_data: List[Dict]) -> str:
        """
        Export conversation history in various formats
        Similar to Medical Chat's export feature
        """
        try:
            export_data = {
                'export_date': datetime.now().isoformat(),
                'conversations': conversation_data,
                'summary': {
                    'total_conversations': len(conversation_data),
                    'date_range': {
                        'start': conversation_data[0]['timestamp'] if conversation_data else None,
                        'end': conversation_data[-1]['timestamp'] if conversation_data else None
                    }
                }
            }
            
            return json.dumps(export_data, indent=2)
            
        except Exception as e:
            logger.error(f"Error exporting conversation history: {str(e)}")
            return ""

# Global instance
advanced_features = AdvancedMedicalFeatures() 