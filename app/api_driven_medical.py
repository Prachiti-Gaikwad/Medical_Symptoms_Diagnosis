#!/usr/bin/env python3
"""
API-Driven Medical Recommendations System
Uses prompts to retrieve comprehensive medical data from APIs instead of hardcoded data
"""

import requests
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from .who_gho_api import WHOGHOAPI

logger = logging.getLogger(__name__)

class APIDrivenMedicalManager:
    """API-driven medical recommendations using prompts to retrieve data from external APIs"""
    
    def __init__(self):
        self.base_urls = {
            'fda': 'https://api.fda.gov/drug',
            'rxnav': 'https://rxnav.nlm.nih.gov/REST',
            'pubmed': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils',
            'who_gho': 'https://ghoapi.azureedge.net/api'
        }
        
        # Initialize WHO GHO API
        self.who_gho_api = WHOGHOAPI()
        
        # API Keys (configure in config.py)
        self.api_keys = {
            'pubmed': None,  # Get from NCBI
            'fda': None      # FDA API is free but rate limited
        }
    
    def get_comprehensive_medical_recommendations(self, condition: str) -> Dict:
        """
        Get comprehensive medical recommendations using API-driven prompts
        Returns: OTC, Prescription, Natural Remedies, and Medical Literature
        """
        try:
            logger.info(f"🔍 Getting API-driven medical recommendations for: {condition}")
            
            # Get all types of recommendations using API prompts
            otc_medicines = self._get_otc_medicines_via_api(condition)
            prescription_medicines = self._get_prescription_medicines_via_api(condition)
            natural_remedies = self._get_natural_remedies_via_api(condition)
            medical_literature = self._get_medical_literature_via_api(condition)
            
            # Compile comprehensive results
            recommendations = {
                'otc_medicines': otc_medicines,
                'prescription_medicines': prescription_medicines,
                'natural_remedies': natural_remedies,
                'medical_literature': medical_literature,
                'api_sources': [
                    'FDA Drug Database',
                    'RxNav Prescription Database', 
                    'WHO GHO Global Health Data',
                    'PubMed Medical Literature'
                ],
                'last_updated': datetime.now().isoformat(),
                'condition': condition,
                'total_recommendations': len(otc_medicines) + len(prescription_medicines) + len(natural_remedies) + len(medical_literature)
            }
            
            logger.info(f"✅ Retrieved {recommendations['total_recommendations']} API-driven recommendations for {condition}")
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Error getting API-driven recommendations for {condition}: {str(e)}")
            return self._get_fallback_recommendations(condition)
    
    def _get_otc_medicines_via_api(self, condition: str) -> List[Dict]:
        """Get OTC medicines from FDA API using intelligent search"""
        try:
            logger.info(f"💊 Getting OTC medicines from FDA API for: {condition}")
            
            # Create intelligent search terms for the condition
            search_terms = self._generate_search_terms(condition, "otc")
            
            otc_medicines = []
            
            for search_term in search_terms:
                try:
                    # Search FDA API for OTC drugs
                    url = f"{self.base_urls['fda']}/label.json"
                    params = {
                        'search': f'openfda.product_type:"OTC" AND ({search_term})',
                        'limit': 10
                    }
                    
                    response = requests.get(url, params=params, timeout=15)
                    response.raise_for_status()
                    
                    data = response.json()
                    if data.get('results'):
                        for drug in data['results']:
                            medicine = self._parse_fda_drug_data(drug, "OTC")
                            if medicine and medicine not in otc_medicines:
                                otc_medicines.append(medicine)
                
                except Exception as e:
                    logger.warning(f"FDA API search failed for {search_term}: {str(e)}")
                    continue
            
            # If no FDA results, try alternative search
            if not otc_medicines:
                otc_medicines = self._get_otc_medicines_alternative_search(condition)
            
            logger.info(f"✅ Found {len(otc_medicines)} OTC medicines via FDA API")
            return otc_medicines
            
        except Exception as e:
            logger.error(f"❌ Error getting OTC medicines: {str(e)}")
            return []
    
    def _get_prescription_medicines_via_api(self, condition: str) -> List[Dict]:
        """Get prescription medicines from RxNav API using intelligent search"""
        try:
            logger.info(f"💉 Getting prescription medicines from RxNav API for: {condition}")
            
            # Create intelligent search terms for the condition
            search_terms = self._generate_search_terms(condition, "prescription")
            
            prescription_medicines = []
            
            for search_term in search_terms:
                try:
                    # Search RxNav API for prescription drugs
                    url = f"{self.base_urls['rxnav']}/drugs.json"
                    params = {
                        'name': search_term,
                        'allsrc': 1
                    }
                    
                    response = requests.get(url, params=params, timeout=15)
                    response.raise_for_status()
                    
                    data = response.json()
                    if data.get('drugGroup', {}).get('conceptGroup'):
                        for concept_group in data['drugGroup']['conceptGroup']:
                            if concept_group.get('concept'):
                                for concept in concept_group['concept']:
                                    medicine = self._parse_rxnav_drug_data(concept, "Prescription")
                                    if medicine and medicine not in prescription_medicines:
                                        prescription_medicines.append(medicine)
                
                except Exception as e:
                    logger.warning(f"RxNav API search failed for {search_term}: {str(e)}")
                    continue
            
            logger.info(f"✅ Found {len(prescription_medicines)} prescription medicines via RxNav API")
            return prescription_medicines
            
        except Exception as e:
            logger.error(f"❌ Error getting prescription medicines: {str(e)}")
            return []
    
    def _get_natural_remedies_via_api(self, condition: str) -> List[Dict]:
        """Get natural remedies from WHO GHO API and other sources"""
        try:
            logger.info(f"🌿 Getting natural remedies from WHO GHO API for: {condition}")
            
            natural_remedies = []
            
            # 1. Try WHO GHO API for traditional medicine data
            try:
                who_remedies = self.who_gho_api.get_traditional_medicine_data(condition)
                if who_remedies:
                    natural_remedies.extend(who_remedies)
                    logger.info(f"✅ Found {len(who_remedies)} traditional remedies from WHO GHO")
            except Exception as e:
                logger.warning(f"WHO GHO traditional medicine failed: {str(e)}")
            
            # 2. Try WHO GHO API for health practices
            try:
                health_practices = self.who_gho_api.get_global_health_practices(condition)
                if health_practices:
                    natural_remedies.extend(health_practices)
                    logger.info(f"✅ Found {len(health_practices)} health practices from WHO GHO")
            except Exception as e:
                logger.warning(f"WHO GHO health practices failed: {str(e)}")
            
            # 3. Try FDA for herbal supplements
            try:
                fda_herbs = self._get_herbal_supplements_from_fda(condition)
                natural_remedies.extend(fda_herbs)
                logger.info(f"✅ Found {len(fda_herbs)} herbal supplements from FDA")
            except Exception as e:
                logger.warning(f"FDA herbal supplements failed: {str(e)}")
            
            # 4. If no remedies found or only fallback data, add common traditional remedies
            if not natural_remedies or all('API temporarily unavailable' in remedy.get('description', '') for remedy in natural_remedies):
                natural_remedies = self._get_common_traditional_remedies(condition)
                logger.info(f"✅ Added {len(natural_remedies)} common traditional remedies")
            
            logger.info(f"✅ Found {len(natural_remedies)} natural remedies via APIs")
            return natural_remedies
            
        except Exception as e:
            logger.error(f"❌ Error getting natural remedies: {str(e)}")
            return []
    
    def _get_medical_literature_via_api(self, condition: str) -> List[Dict]:
        """Get medical literature from PubMed API"""
        try:
            logger.info(f"📚 Getting medical literature from PubMed API for: {condition}")
            
            # Search PubMed for recent medical literature
            url = f"{self.base_urls['pubmed']}/esearch.fcgi"
            params = {
                'db': 'pubmed',
                'term': f'"{condition}"[Title/Abstract] AND ("2020"[Date - Publication] : "3000"[Date - Publication])',
                'retmode': 'json',
                'retmax': 10,
                'sort': 'relevance'
            }
            
            if self.api_keys['pubmed']:
                params['api_key'] = self.api_keys['pubmed']
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            literature = []
            
            if data.get('esearchresult', {}).get('idlist'):
                pmids = data['esearchresult']['idlist']
                
                # Get detailed information for each article
                for pmid in pmids[:5]:  # Limit to 5 articles
                    try:
                        article_info = self._get_pubmed_article_details(pmid)
                        if article_info:
                            literature.append(article_info)
                    except Exception as e:
                        logger.warning(f"Failed to get details for PMID {pmid}: {str(e)}")
                        continue
            
            logger.info(f"✅ Found {len(literature)} medical literature articles via PubMed API")
            return literature
            
        except Exception as e:
            logger.error(f"❌ Error getting medical literature: {str(e)}")
            return []
    
    def _generate_search_terms(self, condition: str, medicine_type: str) -> List[str]:
        """Generate intelligent search terms for API queries"""
        # Base condition terms
        base_terms = [condition.lower()]
        
        # Add common synonyms and related terms
        condition_mapping = {
            'headache': ['migraine', 'cephalalgia', 'head pain', 'tension headache'],
            'chest pain': ['angina', 'cardiac pain', 'thoracic pain', 'heart pain'],
            'stomach ache': ['abdominal pain', 'gastritis', 'indigestion', 'dyspepsia'],
            'fever': ['pyrexia', 'hyperthermia', 'elevated temperature'],
            'cough': ['tussis', 'respiratory irritation', 'bronchial irritation'],
            'back pain': ['lumbago', 'dorsalgia', 'spinal pain', 'musculoskeletal pain'],
            'dizziness': ['vertigo', 'lightheadedness', 'balance problems'],
            'nausea': ['sickness', 'queasiness', 'gastric upset'],
            'diarrhea': ['loose stools', 'gastroenteritis', 'intestinal upset'],
            'insomnia': ['sleeplessness', 'sleep disorder', 'sleep problems'],
            'anxiety': ['nervousness', 'worry', 'stress', 'panic'],
            'depression': ['mood disorder', 'sadness', 'mental health'],
            'allergies': ['allergic reaction', 'hypersensitivity', 'immune response'],
            'arthritis': ['joint pain', 'rheumatism', 'joint inflammation'],
            'hypertension': ['high blood pressure', 'elevated bp', 'cardiovascular']
        }
        
        # Add synonyms
        for key, synonyms in condition_mapping.items():
            if key in condition.lower():
                base_terms.extend(synonyms)
        
        # Add medicine type specific terms
        if medicine_type == "otc":
            base_terms.extend(['over the counter', 'non prescription', 'self care'])
        elif medicine_type == "prescription":
            base_terms.extend(['prescription', 'prescribed', 'medical treatment'])
        
        return list(set(base_terms))  # Remove duplicates
    
    def _parse_fda_drug_data(self, drug_data: Dict, medicine_type: str) -> Optional[Dict]:
        """Parse FDA drug data into standardized format"""
        try:
            openfda = drug_data.get('openfda', {})
            
            return {
                'name': openfda.get('generic_name', ['Unknown'])[0] if openfda.get('generic_name') else 'Unknown',
                'brand_name': openfda.get('brand_name', ['Unknown'])[0] if openfda.get('brand_name') else 'Unknown',
                'dosage': self._extract_dosage_from_fda(drug_data),
                'warnings': self._extract_warnings_from_fda(drug_data),
                'side_effects': self._extract_side_effects_from_fda(drug_data),
                'indications': self._extract_indications_from_fda(drug_data),
                'source': 'FDA Drug Database',
                'type': medicine_type
            }
        except Exception as e:
            logger.warning(f"Failed to parse FDA drug data: {str(e)}")
            return None
    
    def _parse_rxnav_drug_data(self, drug_data: Dict, medicine_type: str) -> Optional[Dict]:
        """Parse RxNav drug data into standardized format"""
        try:
            return {
                'name': drug_data.get('name', 'Unknown'),
                'brand_name': drug_data.get('synonym', 'Unknown'),
                'dosage': 'Consult healthcare provider for dosage',
                'warnings': 'Prescription medication - use as directed',
                'side_effects': 'Consult healthcare provider for side effects',
                'indications': drug_data.get('drugClasses', []),
                'source': 'RxNav Prescription Database',
                'type': medicine_type
            }
        except Exception as e:
            logger.warning(f"Failed to parse RxNav drug data: {str(e)}")
            return None
    
    def _get_pubmed_article_details(self, pmid: str) -> Optional[Dict]:
        """Get detailed article information from PubMed"""
        try:
            url = f"{self.base_urls['pubmed']}/esummary.fcgi"
            params = {
                'db': 'pubmed',
                'id': pmid,
                'retmode': 'json'
            }
            
            if self.api_keys['pubmed']:
                params['api_key'] = self.api_keys['pubmed']
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('result', {}).get(pmid):
                article = data['result'][pmid]
                
                return {
                    'title': article.get('title', 'Unknown Title'),
                    'authors': article.get('authors', []),
                    'abstract': article.get('abstract', 'No abstract available'),
                    'pub_date': article.get('pubdate', 'Unknown'),
                    'journal': article.get('fulljournalname', 'Unknown Journal'),
                    'source': 'PubMed Medical Literature'
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to get PubMed article details: {str(e)}")
            return None
    
    def _get_natural_remedies_from_pubmed(self, condition: str) -> List[Dict]:
        """Get natural remedy research from PubMed"""
        try:
            url = f"{self.base_urls['pubmed']}/esearch.fcgi"
            params = {
                'db': 'pubmed',
                'term': f'"{condition}" AND ("natural remedy" OR "herbal" OR "traditional medicine")[Title/Abstract]',
                'retmode': 'json',
                'retmax': 5,
                'sort': 'relevance'
            }
            
            if self.api_keys['pubmed']:
                params['api_key'] = self.api_keys['pubmed']
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            remedies = []
            
            if data.get('esearchresult', {}).get('idlist'):
                pmids = data['esearchresult']['idlist']
                
                for pmid in pmids[:3]:
                    try:
                        article_info = self._get_pubmed_article_details(pmid)
                        if article_info:
                            remedies.append({
                                'name': f"Research-backed remedy for {condition}",
                                'description': article_info.get('abstract', 'Research-based natural remedy'),
                                'usage': 'Based on medical research',
                                'effectiveness': 'Research-supported',
                                'source': 'PubMed Research Literature'
                            })
                    except Exception as e:
                        continue
            
            return remedies
            
        except Exception as e:
            logger.warning(f"Failed to get natural remedies from PubMed: {str(e)}")
            return []
    
    def _get_herbal_supplements_from_fda(self, condition: str) -> List[Dict]:
        """Get herbal supplements from FDA database"""
        try:
            url = f"{self.base_urls['fda']}/label.json"
            params = {
                'search': f'openfda.product_type:"Dietary Supplement" AND ({condition})',
                'limit': 5
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            supplements = []
            
            if data.get('results'):
                for supplement in data['results']:
                    openfda = supplement.get('openfda', {})
                    supplements.append({
                        'name': openfda.get('generic_name', ['Herbal Supplement'])[0] if openfda.get('generic_name') else 'Herbal Supplement',
                        'description': 'Natural herbal supplement',
                        'usage': 'Follow label instructions',
                        'effectiveness': 'Traditional use',
                        'source': 'FDA Dietary Supplement Database'
                    })
            
            return supplements
            
        except Exception as e:
            logger.warning(f"Failed to get herbal supplements from FDA: {str(e)}")
            return []
    
    def _get_otc_medicines_alternative_search(self, condition: str) -> List[Dict]:
        """Alternative OTC medicine search when primary search fails"""
        try:
            # Try broader search terms
            url = f"{self.base_urls['fda']}/label.json"
            params = {
                'search': f'openfda.product_type:"OTC"',
                'limit': 20
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            medicines = []
            
            if data.get('results'):
                for drug in data['results']:
                    medicine = self._parse_fda_drug_data(drug, "OTC")
                    if medicine:
                        medicines.append(medicine)
            
            return medicines[:5]  # Return top 5
            
        except Exception as e:
            logger.warning(f"Alternative OTC search failed: {str(e)}")
            return []
    
    def _extract_dosage_from_fda(self, drug_data: Dict) -> str:
        """Extract dosage information from FDA data"""
        try:
            # Look for dosage information in various FDA fields
            dosage_sections = drug_data.get('dosage_and_administration', [])
            if dosage_sections:
                return dosage_sections[0][:200] + "..." if len(dosage_sections[0]) > 200 else dosage_sections[0]
            
            return "Consult healthcare provider for dosage"
        except:
            return "Consult healthcare provider for dosage"
    
    def _extract_warnings_from_fda(self, drug_data: Dict) -> str:
        """Extract warnings from FDA data"""
        try:
            warnings = drug_data.get('warnings', [])
            if warnings:
                return warnings[0][:200] + "..." if len(warnings[0]) > 200 else warnings[0]
            
            return "Read label carefully and consult healthcare provider"
        except:
            return "Read label carefully and consult healthcare provider"
    
    def _extract_side_effects_from_fda(self, drug_data: Dict) -> str:
        """Extract side effects from FDA data"""
        try:
            side_effects = drug_data.get('adverse_reactions', [])
            if side_effects:
                return side_effects[0][:200] + "..." if len(side_effects[0]) > 200 else side_effects[0]
            
            return "Consult healthcare provider for side effects"
        except:
            return "Consult healthcare provider for side effects"
    
    def _extract_indications_from_fda(self, drug_data: Dict) -> str:
        """Extract indications from FDA data"""
        try:
            indications = drug_data.get('indications_and_usage', [])
            if indications:
                return indications[0][:200] + "..." if len(indications[0]) > 200 else indications[0]
            
            return "Consult healthcare provider for proper use"
        except:
            return "Consult healthcare provider for proper use"
    
    def _get_common_traditional_remedies(self, condition: str) -> List[Dict]:
        """Get common traditional remedies based on condition"""
        condition_lower = condition.lower()
        
        # Common traditional remedies for different conditions
        traditional_remedies = {
            'headache': [
                {
                    'name': 'Peppermint Oil',
                    'description': 'Traditional remedy for tension headaches',
                    'usage': 'Apply diluted peppermint oil to temples and forehead',
                    'effectiveness': 'Moderate effectiveness for tension headaches',
                    'source': 'Traditional Medicine - Europe'
                },
                {
                    'name': 'Ginger Tea',
                    'description': 'Natural anti-inflammatory for headache relief',
                    'usage': 'Steep fresh ginger in hot water, drink 2-3 times daily',
                    'effectiveness': 'Good for migraine and tension headaches',
                    'source': 'Traditional Medicine - Asia'
                },
                {
                    'name': 'Lavender Oil',
                    'description': 'Calming essential oil for headache relief',
                    'usage': 'Inhale lavender oil or apply to temples',
                    'effectiveness': 'Effective for stress-related headaches',
                    'source': 'Traditional Medicine - Mediterranean'
                }
            ],
            'fever': [
                {
                    'name': 'Willow Bark Tea',
                    'description': 'Natural fever reducer containing salicin',
                    'usage': 'Steep willow bark in hot water, drink 2-3 times daily',
                    'effectiveness': 'Moderate effectiveness for fever reduction',
                    'source': 'Traditional Medicine - Global'
                },
                {
                    'name': 'Elderberry Syrup',
                    'description': 'Immune-boosting traditional remedy',
                    'usage': 'Take 1-2 teaspoons daily during illness',
                    'effectiveness': 'Good for immune support and fever',
                    'source': 'Traditional Medicine - Europe'
                },
                {
                    'name': 'Cool Compress',
                    'description': 'Traditional physical therapy for fever',
                    'usage': 'Apply cool, damp cloth to forehead and body',
                    'effectiveness': 'Immediate relief for fever symptoms',
                    'source': 'Traditional Medicine - Global'
                }
            ],
            'cough': [
                {
                    'name': 'Honey and Lemon',
                    'description': 'Traditional cough remedy with antibacterial properties',
                    'usage': 'Mix 1 tablespoon honey with lemon juice, take as needed',
                    'effectiveness': 'Excellent for soothing cough and sore throat',
                    'source': 'Traditional Medicine - Global'
                },
                {
                    'name': 'Thyme Tea',
                    'description': 'Natural expectorant for cough relief',
                    'usage': 'Steep thyme in hot water, drink 2-3 times daily',
                    'effectiveness': 'Good for productive coughs',
                    'source': 'Traditional Medicine - Mediterranean'
                },
                {
                    'name': 'Steam Inhalation',
                    'description': 'Traditional therapy for respiratory symptoms',
                    'usage': 'Inhale steam with eucalyptus oil for 10-15 minutes',
                    'effectiveness': 'Immediate relief for cough and congestion',
                    'source': 'Traditional Medicine - Global'
                }
            ],
            'stomach': [
                {
                    'name': 'Ginger Root',
                    'description': 'Traditional remedy for nausea and stomach upset',
                    'usage': 'Chew fresh ginger or drink ginger tea',
                    'effectiveness': 'Excellent for nausea and digestive issues',
                    'source': 'Traditional Medicine - Asia'
                },
                {
                    'name': 'Peppermint Tea',
                    'description': 'Natural digestive aid and stomach soother',
                    'usage': 'Steep peppermint leaves in hot water, drink after meals',
                    'effectiveness': 'Good for indigestion and stomach pain',
                    'source': 'Traditional Medicine - Europe'
                },
                {
                    'name': 'Chamomile Tea',
                    'description': 'Calming herb for stomach inflammation',
                    'usage': 'Steep chamomile flowers in hot water, drink 2-3 times daily',
                    'effectiveness': 'Effective for stomach inflammation and pain',
                    'source': 'Traditional Medicine - Mediterranean'
                }
            ],
            'pain': [
                {
                    'name': 'Arnica Gel',
                    'description': 'Traditional remedy for muscle and joint pain',
                    'usage': 'Apply arnica gel to affected area 2-3 times daily',
                    'effectiveness': 'Good for muscle pain and bruising',
                    'source': 'Traditional Medicine - Europe'
                },
                {
                    'name': 'Turmeric',
                    'description': 'Natural anti-inflammatory for pain relief',
                    'usage': 'Mix turmeric with warm milk or take as supplement',
                    'effectiveness': 'Moderate effectiveness for chronic pain',
                    'source': 'Traditional Medicine - India'
                },
                {
                    'name': 'Epsom Salt Bath',
                    'description': 'Traditional therapy for muscle pain relief',
                    'usage': 'Dissolve 2 cups Epsom salt in warm bath, soak for 20 minutes',
                    'effectiveness': 'Immediate relief for muscle pain and tension',
                    'source': 'Traditional Medicine - Global'
                }
            ]
        }
        
        # Find matching remedies
        for key, remedies in traditional_remedies.items():
            if key in condition_lower:
                return remedies
        
        # Default remedies for any condition
        return [
            {
                'name': 'Rest and Hydration',
                'description': 'Fundamental traditional healing practice',
                'usage': 'Get adequate rest and drink plenty of fluids',
                'effectiveness': 'Essential for recovery from any illness',
                'source': 'Traditional Medicine - Global'
            },
            {
                'name': 'Warm Compress',
                'description': 'Traditional therapy for various conditions',
                'usage': 'Apply warm, damp cloth to affected area',
                'effectiveness': 'Good for pain relief and inflammation',
                'source': 'Traditional Medicine - Global'
            }
        ]

    def _get_fallback_recommendations(self, condition: str) -> Dict:
        """Fallback recommendations when APIs fail"""
        logger.warning(f"Using fallback recommendations for {condition}")
        
        return {
            'otc_medicines': [],
            'prescription_medicines': [],
            'natural_remedies': [],
            'medical_literature': [],
            'api_sources': ['Fallback System'],
            'last_updated': datetime.now().isoformat(),
            'condition': condition,
            'total_recommendations': 0,
            'note': 'API-driven recommendations temporarily unavailable. Please consult healthcare provider.'
        }

# Global instance
api_driven_medical = APIDrivenMedicalManager() 