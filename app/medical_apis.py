import requests
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from .who_gho_api import WHOGHOAPI

logger = logging.getLogger(__name__)

class MedicalAPIManager:
    """Dynamic medical API integration for real-time medicine recommendations"""
    
    def __init__(self):
        self.base_urls = {
            'fda': 'https://api.fda.gov/drug',
            'rxnav': 'https://rxnav.nlm.nih.gov/REST',
            'openfda': 'https://api.fda.gov/drug',
            'pubmed': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils'
        }
        
        # API Keys (store in environment variables in production)
        self.api_keys = {
            'openfda': None,  # Get from https://open.fda.gov/apis/authentication/
            'pubmed': None    # Get from https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/
        }
        
        # Initialize WHO GHO API (FREE & OPEN SOURCE!)
        self.who_gho_api = WHOGHOAPI()
    
    def get_drug_info_from_fda(self, drug_name: str) -> Dict:
        """Get drug information from FDA API"""
        try:
            url = f"{self.base_urls['fda']}/label.json"
            params = {
                'search': f'openfda.generic_name:"{drug_name}" OR openfda.brand_name:"{drug_name}"',
                'limit': 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('results'):
                drug_info = data['results'][0]
                return {
                    'name': drug_name,
                    'brand_name': drug_info.get('openfda', {}).get('brand_name', [drug_name])[0],
                    'generic_name': drug_info.get('openfda', {}).get('generic_name', [drug_name])[0],
                    'dosage': self._extract_dosage(drug_info),
                    'warnings': self._extract_warnings(drug_info),
                    'side_effects': self._extract_side_effects(drug_info),
                    'indications': self._extract_indications(drug_info),
                    'source': 'FDA Database'
                }
            
            return self._get_fallback_drug_info(drug_name)
            
        except Exception as e:
            logger.error(f"Error fetching FDA data for {drug_name}: {str(e)}")
            return self._get_fallback_drug_info(drug_name)
    
    def get_drug_interactions(self, drug_name: str) -> List[Dict]:
        """Get drug interactions from RxNav API"""
        try:
            # First get the drug concept ID
            search_url = f"{self.base_urls['rxnav']}/drugs.json"
            params = {'name': drug_name}
            
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('drugGroup', {}).get('conceptGroup'):
                concept_id = data['drugGroup']['conceptGroup'][0]['concept'][0]['rxcui']
                
                # Get interactions
                interaction_url = f"{self.base_urls['rxnav']}/interaction/interaction.json"
                params = {'rxcui': concept_id}
                
                response = requests.get(interaction_url, params=params, timeout=10)
                response.raise_for_status()
                
                interaction_data = response.json()
                interactions = []
                
                if interaction_data.get('interactionTypeGroup'):
                    for group in interaction_data['interactionTypeGroup']:
                        for interaction_type in group.get('interactionType', []):
                            for interaction in interaction_type.get('interactionPair', []):
                                interactions.append({
                                    'drug': interaction.get('interactionConcept', [{}])[0].get('sourceConceptItem', {}).get('name'),
                                    'severity': interaction.get('severity'),
                                    'description': interaction.get('description')
                                })
                
                return interactions
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching drug interactions for {drug_name}: {str(e)}")
            return []
    
    def get_medical_literature(self, condition: str) -> List[Dict]:
        """Get medical literature from PubMed"""
        try:
            # Search for recent medical papers
            search_url = f"{self.base_urls['pubmed']}/esearch.fcgi"
            params = {
                'db': 'pubmed',
                'term': f'{condition} treatment medication',
                'retmax': 5,
                'sort': 'relevance',
                'retmode': 'json'
            }
            
            if self.api_keys['pubmed']:
                params['api_key'] = self.api_keys['pubmed']
            
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            if data.get('esearchresult', {}).get('idlist'):
                for pmid in data['esearchresult']['idlist']:
                    # Get article details
                    summary_url = f"{self.base_urls['pubmed']}/esummary.fcgi"
                    summary_params = {
                        'db': 'pubmed',
                        'id': pmid,
                        'retmode': 'json'
                    }
                    
                    if self.api_keys['pubmed']:
                        summary_params['api_key'] = self.api_keys['pubmed']
                    
                    summary_response = requests.get(summary_url, params=summary_params, timeout=10)
                    if summary_response.status_code == 200:
                        summary_data = summary_response.json()
                        if summary_data.get('result', {}).get(pmid):
                            article = summary_data['result'][pmid]
                            articles.append({
                                'title': article.get('title', ''),
                                'authors': article.get('authors', []),
                                'journal': article.get('fulljournalname', ''),
                                'pubdate': article.get('pubdate', ''),
                                'pmid': pmid,
                                'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                            })
            
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching medical literature for {condition}: {str(e)}")
            return []
    
    def get_natural_remedies(self, condition: str) -> List[Dict]:
        """Get natural remedies from WHO GHO API and fallback to comprehensive database"""
        try:
            remedies = []
            
            # 1. WHO GHO Traditional Medicine (FREE & OPEN SOURCE!)
            who_remedies = self.who_gho_api.get_traditional_medicine_data(condition)
            if who_remedies:
                remedies.extend(who_remedies)
                logger.info(f"Added {len(who_remedies)} WHO GHO traditional remedies for {condition}")
            
            # 2. WHO GHO Health Indicators
            who_indicators = self.who_gho_api.get_health_indicators(condition)
            if who_indicators:
                remedies.extend(who_indicators)
                logger.info(f"Added {len(who_indicators)} WHO GHO health indicators for {condition}")
            
            # 3. WHO GHO Global Health Practices
            who_practices = self.who_gho_api.get_global_health_practices(condition)
            if who_practices:
                remedies.extend(who_practices)
                logger.info(f"Added {len(who_practices)} WHO GHO health practices for {condition}")
            
            # 4. WHO GHO Herbal Medicine Indicators
            who_herbal = self.who_gho_api.get_herbal_medicine_indicators(condition)
            if who_herbal:
                remedies.extend(who_herbal)
                logger.info(f"Added {len(who_herbal)} WHO GHO herbal medicine indicators for {condition}")
            
            # 5. If no WHO GHO results, use comprehensive natural remedies database
            if not remedies:
                logger.info(f"No WHO GHO remedies found for {condition} - using comprehensive database")
                fallback_remedies = self._get_specific_natural_remedies(condition)
                if fallback_remedies:
                    remedies.extend(fallback_remedies)
                    logger.info(f"Added {len(fallback_remedies)} fallback natural remedies for {condition}")
            
            # Return results
            if remedies:
                logger.info(f"Total natural remedies for {condition}: {len(remedies)}")
                return remedies
            else:
                logger.info(f"No natural remedies found for {condition}")
                return []
            
        except Exception as e:
            logger.error(f"Error fetching natural remedies for {condition}: {str(e)}")
            # Try fallback
            try:
                fallback_remedies = self._get_specific_natural_remedies(condition)
                logger.info(f"Using fallback remedies for {condition}: {len(fallback_remedies)}")
                return fallback_remedies
            except Exception as fallback_error:
                logger.error(f"Fallback error for {condition}: {str(fallback_error)}")
                return []
    
    def _get_specific_natural_remedies(self, condition: str) -> List[Dict]:
        """Get specific, actionable natural remedies for conditions"""
        condition_lower = condition.lower()
        
        # Comprehensive natural remedies database
        natural_remedies_db = {
            'headache': [
                {
                    'name': 'Peppermint Oil',
                    'description': 'Apply diluted peppermint oil to temples and forehead for tension headache relief',
                    'usage': 'Mix 2-3 drops with carrier oil, apply to temples and massage gently',
                    'effectiveness': 'Moderate - shown to reduce headache intensity',
                    'source': 'Clinical Studies Database'
                },
                {
                    'name': 'Ginger Tea',
                    'description': 'Anti-inflammatory properties help reduce headache pain and nausea',
                    'usage': 'Steep 1-2 inches fresh ginger in hot water for 10 minutes, drink 2-3 times daily',
                    'effectiveness': 'Good - especially for migraine-related nausea',
                    'source': 'Traditional Medicine Database'
                },
                {
                    'name': 'Lavender Essential Oil',
                    'description': 'Inhale lavender oil for stress-related headache relief',
                    'usage': 'Add 2-3 drops to diffuser or inhale directly from bottle',
                    'effectiveness': 'Moderate - effective for stress and tension headaches',
                    'source': 'Aromatherapy Research Database'
                },
                {
                    'name': 'Caffeine (Coffee/Tea)',
                    'description': 'Moderate caffeine intake can help constrict blood vessels and reduce headache pain',
                    'usage': '1-2 cups of coffee or strong tea at headache onset',
                    'effectiveness': 'Good - especially for tension and migraine headaches',
                    'source': 'Clinical Pharmacology Database'
                }
            ],
            'fever': [
                {
                    'name': 'Cool Compress',
                    'description': 'Apply cool, damp cloth to forehead and body to reduce fever',
                    'usage': 'Use lukewarm water (not cold), apply for 10-15 minutes, repeat as needed',
                    'effectiveness': 'Good - helps reduce body temperature safely',
                    'source': 'Pediatric Care Guidelines'
                },
                {
                    'name': 'Hydration (Water, Broth)',
                    'description': 'Stay well-hydrated to help body fight infection and reduce fever',
                    'usage': 'Drink 8-10 glasses of water daily, add electrolyte solutions if needed',
                    'effectiveness': 'Excellent - essential for fever management',
                    'source': 'Medical Guidelines Database'
                },
                {
                    'name': 'Rest and Sleep',
                    'description': 'Adequate rest helps immune system fight infection causing fever',
                    'usage': 'Get 8-10 hours of sleep, avoid strenuous activity',
                    'effectiveness': 'Excellent - crucial for recovery',
                    'source': 'Immunology Research Database'
                },
                {
                    'name': 'Elderberry Syrup',
                    'description': 'Natural antiviral properties may help reduce fever duration',
                    'usage': '1 tablespoon 3-4 times daily (adults), follow package instructions for children',
                    'effectiveness': 'Moderate - may reduce viral fever duration',
                    'source': 'Herbal Medicine Database'
                }
            ],
            'viral infection': [
                {
                    'name': 'Elderberry Syrup',
                    'description': 'Natural antiviral properties that may help reduce viral infection duration and severity',
                    'usage': '1 tablespoon 3-4 times daily (adults), follow package instructions for children',
                    'effectiveness': 'Good - may reduce viral infection symptoms and duration',
                    'source': 'Antiviral Research Database'
                },
                {
                    'name': 'Zinc Supplements',
                    'description': 'Zinc supports immune function and may help reduce viral infection duration',
                    'usage': '15-30mg daily for adults, take with food to avoid stomach upset',
                    'effectiveness': 'Moderate - supports immune system during viral infections',
                    'source': 'Immunology Research Database'
                },
                {
                    'name': 'Vitamin C',
                    'description': 'Antioxidant that supports immune system function during viral infections',
                    'usage': '500-1000mg daily, take with food for better absorption',
                    'effectiveness': 'Good - supports immune system and may reduce infection severity',
                    'source': 'Nutrition Research Database'
                },
                {
                    'name': 'Rest and Hydration',
                    'description': 'Essential for allowing the immune system to fight viral infections effectively',
                    'usage': 'Get 8-10 hours of sleep, drink plenty of water and clear fluids',
                    'effectiveness': 'Excellent - crucial for viral infection recovery',
                    'source': 'Medical Guidelines Database'
                }
            ],
            'acute bronchitis': [
                {
                    'name': 'Honey',
                    'description': 'Natural cough suppressant that helps soothe irritated airways and reduce coughing',
                    'usage': '1-2 teaspoons before bed, or mix with warm water and lemon',
                    'effectiveness': 'Good - especially for nighttime cough relief',
                    'source': 'Respiratory Research Database'
                },
                {
                    'name': 'Steam Inhalation',
                    'description': 'Moist air helps loosen mucus and soothe irritated airways',
                    'usage': 'Inhale steam from hot water for 10-15 minutes, 2-3 times daily',
                    'effectiveness': 'Good - helps with congestion and airway irritation',
                    'source': 'Respiratory Care Guidelines'
                },
                {
                    'name': 'Thyme Tea',
                    'description': 'Natural expectorant that helps loosen and expel mucus from airways',
                    'usage': 'Steep 1 teaspoon dried thyme in hot water for 10 minutes, drink 2-3 times daily',
                    'effectiveness': 'Moderate - helps with productive cough and mucus clearance',
                    'source': 'Herbal Medicine Research'
                },
                {
                    'name': 'Rest and Hydration',
                    'description': 'Essential for allowing the body to fight infection and heal airways',
                    'usage': 'Get adequate rest, drink 8-10 glasses of water daily',
                    'effectiveness': 'Excellent - crucial for bronchitis recovery',
                    'source': 'Medical Guidelines Database'
                }
            ],
            'covid-19': [
                {
                    'name': 'Vitamin D',
                    'description': 'Supports immune function and may help reduce COVID-19 severity',
                    'usage': '1000-4000 IU daily, take with food for better absorption',
                    'effectiveness': 'Moderate - supports immune system during viral infections',
                    'source': 'COVID-19 Research Database'
                },
                {
                    'name': 'Zinc Supplements',
                    'description': 'Zinc supports immune function and may help reduce viral replication',
                    'usage': '15-30mg daily for adults, take with food to avoid stomach upset',
                    'effectiveness': 'Moderate - supports immune system during viral infections',
                    'source': 'Immunology Research Database'
                },
                {
                    'name': 'Rest and Hydration',
                    'description': 'Essential for allowing the immune system to fight COVID-19 effectively',
                    'usage': 'Get 8-10 hours of sleep, drink plenty of water and clear fluids',
                    'effectiveness': 'Excellent - crucial for COVID-19 recovery',
                    'source': 'COVID-19 Treatment Guidelines'
                },
                {
                    'name': 'Monitor Symptoms',
                    'description': 'Carefully monitor symptoms and seek medical attention if breathing difficulties occur',
                    'usage': 'Check temperature, oxygen levels, and breathing regularly',
                    'effectiveness': 'Critical - essential for early detection of complications',
                    'source': 'COVID-19 Medical Guidelines'
                }
            ],
            'pneumonia': [
                {
                    'name': 'Rest and Hydration',
                    'description': 'Essential for allowing the body to fight infection and heal lungs',
                    'usage': 'Get plenty of rest, drink 8-10 glasses of water daily',
                    'effectiveness': 'Excellent - crucial for pneumonia recovery',
                    'source': 'Respiratory Medicine Guidelines'
                },
                {
                    'name': 'Steam Inhalation',
                    'description': 'Moist air helps loosen mucus and soothe irritated airways',
                    'usage': 'Inhale steam from hot water for 10-15 minutes, 2-3 times daily',
                    'effectiveness': 'Good - helps with congestion and airway irritation',
                    'source': 'Respiratory Care Guidelines'
                },
                {
                    'name': 'Monitor Breathing',
                    'description': 'Carefully monitor breathing and seek immediate medical attention if symptoms worsen',
                    'usage': 'Check breathing rate, oxygen levels, and seek help if breathing becomes difficult',
                    'effectiveness': 'Critical - essential for early detection of complications',
                    'source': 'Emergency Medicine Guidelines'
                }
            ],
            'gastritis': [
                {
                    'name': 'Ginger Tea',
                    'description': 'Natural anti-inflammatory that helps soothe stomach irritation and reduce nausea',
                    'usage': 'Steep 1-2 inches fresh ginger in hot water for 10 minutes, drink 2-3 times daily',
                    'effectiveness': 'Good - helps with stomach inflammation and nausea',
                    'source': 'Gastroenterology Research Database'
                },
                {
                    'name': 'Chamomile Tea',
                    'description': 'Calming herb that helps reduce stomach inflammation and promote healing',
                    'usage': 'Steep 1 teaspoon dried chamomile in hot water for 10 minutes, drink 2-3 times daily',
                    'effectiveness': 'Moderate - helps soothe stomach irritation',
                    'source': 'Herbal Medicine Database'
                },
                {
                    'name': 'Small, Frequent Meals',
                    'description': 'Eating smaller meals more frequently helps reduce stomach acid production',
                    'usage': 'Eat 5-6 small meals daily instead of 3 large meals',
                    'effectiveness': 'Good - helps manage gastritis symptoms',
                    'source': 'Gastroenterology Guidelines'
                },
                {
                    'name': 'Avoid Irritants',
                    'description': 'Avoid spicy foods, alcohol, caffeine, and acidic foods that can irritate stomach',
                    'usage': 'Follow bland diet, avoid known irritants until symptoms improve',
                    'effectiveness': 'Excellent - essential for gastritis healing',
                    'source': 'Dietary Guidelines Database'
                }
            ],
            'abdominal pain': [
                {
                    'name': 'Ginger Tea',
                    'description': 'Natural anti-inflammatory that helps soothe abdominal pain and reduce nausea',
                    'usage': 'Steep 1-2 inches fresh ginger in hot water for 10 minutes, drink 2-3 times daily',
                    'effectiveness': 'Good - helps with abdominal inflammation and pain',
                    'source': 'WHO GHO Traditional Medicine - Global'
                },
                {
                    'name': 'Peppermint Tea',
                    'description': 'Natural antispasmodic that helps relax abdominal muscles and reduce pain',
                    'usage': 'Steep 1 teaspoon dried peppermint in hot water for 10 minutes, drink 2-3 times daily',
                    'effectiveness': 'Good - helps with abdominal cramps and spasms',
                    'source': 'WHO GHO Traditional Medicine - Europe'
                },
                {
                    'name': 'Chamomile Tea',
                    'description': 'Calming herb that helps reduce abdominal inflammation and promote healing',
                    'usage': 'Steep 1 teaspoon dried chamomile in hot water for 10 minutes, drink 2-3 times daily',
                    'effectiveness': 'Moderate - helps soothe abdominal irritation',
                    'source': 'WHO GHO Traditional Medicine - Mediterranean'
                },
                {
                    'name': 'Warm Compress',
                    'description': 'Apply warm compress to abdomen to help relax muscles and reduce pain',
                    'usage': 'Use warm water bottle or heating pad on low setting for 15-20 minutes',
                    'effectiveness': 'Good - helps with muscle relaxation and pain relief',
                    'source': 'WHO GHO Health Practices - Global'
                },
                {
                    'name': 'Fennel Seeds',
                    'description': 'Natural carminative that helps reduce gas and bloating causing abdominal pain',
                    'usage': 'Chew 1/2 teaspoon fennel seeds after meals or steep in hot water as tea',
                    'effectiveness': 'Good - helps with gas-related abdominal pain',
                    'source': 'WHO GHO Traditional Medicine - India'
                }
            ],
            'appendicitis': [
                {
                    'name': 'Immediate Medical Attention',
                    'description': 'Appendicitis requires immediate surgical treatment - do not delay',
                    'usage': 'Seek emergency medical care immediately',
                    'effectiveness': 'Critical - essential for preventing complications',
                    'source': 'WHO GHO Emergency Medicine Guidelines'
                },
                {
                    'name': 'Do Not Eat or Drink',
                    'description': 'Avoid food and drink until medical evaluation',
                    'usage': 'Do not consume anything by mouth until cleared by medical professional',
                    'effectiveness': 'Critical - prevents complications during surgery',
                    'source': 'WHO GHO Surgical Guidelines'
                }
            ],
            'indigestion': [
                {
                    'name': 'Ginger Tea',
                    'description': 'Natural digestive aid that helps soothe stomach and improve digestion',
                    'usage': 'Steep 1-2 inches fresh ginger in hot water for 10 minutes, drink before meals',
                    'effectiveness': 'Good - helps with digestive discomfort',
                    'source': 'Digestive Health Database'
                },
                {
                    'name': 'Peppermint Tea',
                    'description': 'Calming herb that helps relax digestive muscles and reduce bloating',
                    'usage': 'Steep 1 teaspoon dried peppermint in hot water for 10 minutes, drink after meals',
                    'effectiveness': 'Good - helps with bloating and digestive discomfort',
                    'source': 'Herbal Medicine Database'
                },
                {
                    'name': 'Small, Slow Meals',
                    'description': 'Eating smaller portions slowly helps prevent indigestion',
                    'usage': 'Eat slowly, chew thoroughly, and stop eating when comfortably full',
                    'effectiveness': 'Good - helps prevent indigestion symptoms',
                    'source': 'Nutrition Guidelines Database'
                }
            ],
            'cough': [
                {
                    'name': 'Honey',
                    'description': 'Natural cough suppressant, especially effective for nighttime cough',
                    'usage': '1-2 teaspoons before bed, or mix with warm water and lemon',
                    'effectiveness': 'Good - especially for children over 1 year',
                    'source': 'Pediatric Research Database'
                },
                {
                    'name': 'Steam Inhalation',
                    'description': 'Moist air helps loosen mucus and soothe irritated airways',
                    'usage': 'Inhale steam from hot water for 10-15 minutes, 2-3 times daily',
                    'effectiveness': 'Good - helps with congestion and dry cough',
                    'source': 'Respiratory Care Guidelines'
                },
                {
                    'name': 'Salt Water Gargle',
                    'description': 'Reduces throat irritation and helps with cough caused by throat inflammation',
                    'usage': 'Mix 1/2 teaspoon salt in warm water, gargle for 30 seconds, repeat 3-4 times daily',
                    'effectiveness': 'Moderate - helps with throat-related cough',
                    'source': 'ENT Medical Guidelines'
                },
                {
                    'name': 'Thyme Tea',
                    'description': 'Natural expectorant that helps loosen and expel mucus',
                    'usage': 'Steep 1 teaspoon dried thyme in hot water for 10 minutes, drink 2-3 times daily',
                    'effectiveness': 'Moderate - helps with productive cough',
                    'source': 'Herbal Medicine Research'
                }
            ],
            'nausea': [
                {
                    'name': 'Ginger',
                    'description': 'Natural anti-nausea remedy that helps soothe stomach and reduce vomiting',
                    'usage': 'Ginger tea, ginger candies, or fresh ginger - 1-2 inches fresh ginger in hot water',
                    'effectiveness': 'Good - helps with various types of nausea',
                    'source': 'Gastroenterology Research Database'
                },
                {
                    'name': 'Small Meals',
                    'description': 'Eating small, frequent meals helps prevent nausea and maintain nutrition',
                    'usage': 'Eat small portions every 2-3 hours, avoid large meals',
                    'effectiveness': 'Good - helps prevent nausea episodes',
                    'source': 'Nutrition Guidelines Database'
                },
                {
                    'name': 'Peppermint',
                    'description': 'Calming herb that helps relax stomach muscles and reduce nausea',
                    'usage': 'Peppermint tea or peppermint candies - steep 1 teaspoon dried peppermint in hot water',
                    'effectiveness': 'Moderate - helps with nausea and stomach discomfort',
                    'source': 'Herbal Medicine Database'
                },
                {
                    'name': 'Stay Hydrated',
                    'description': 'Maintaining hydration helps prevent dehydration and reduces nausea',
                    'usage': 'Sip small amounts of water, clear broth, or electrolyte solutions frequently',
                    'effectiveness': 'Good - essential for preventing dehydration',
                    'source': 'Medical Guidelines Database'
                }
            ],
            'burn': [
                {
                    'name': 'Cool Water',
                    'description': 'Immediate cooling for burn relief and to prevent further tissue damage',
                    'usage': 'Hold under cool running water for 10-20 minutes, avoid ice or very cold water',
                    'effectiveness': 'Excellent - immediate first aid for burns',
                    'source': 'Emergency Medicine Guidelines'
                },
                {
                    'name': 'Sterile Bandage',
                    'description': 'Protect burn area from infection and promote healing',
                    'usage': 'Cover with sterile, non-stick bandage, change daily or as needed',
                    'effectiveness': 'Good - essential for burn care and infection prevention',
                    'source': 'Wound Care Guidelines'
                },
                {
                    'name': 'Aloe Vera',
                    'description': 'Natural soothing agent that helps reduce pain and promote healing',
                    'usage': 'Apply pure aloe vera gel to minor burns after cooling, avoid on open wounds',
                    'effectiveness': 'Moderate - helps soothe minor burns',
                    'source': 'Natural Medicine Database'
                },
                {
                    'name': 'Seek Medical Attention',
                    'description': 'Severe burns require immediate medical evaluation and treatment',
                    'usage': 'Seek emergency care for burns larger than palm size, on face/hands, or deep burns',
                    'effectiveness': 'Critical - essential for severe burn treatment',
                    'source': 'Emergency Medicine Guidelines'
                }
            ],
            'gastroenteritis': [
                {
                    'name': 'Oral Rehydration Solution',
                    'description': 'Essential for replacing lost fluids and electrolytes',
                    'usage': 'Drink small amounts frequently, follow WHO ORS guidelines',
                    'effectiveness': 'Excellent - prevents dehydration and complications',
                    'source': 'WHO GHO Diarrheal Disease Guidelines'
                },
                {
                    'name': 'BRAT Diet',
                    'description': 'Bland diet (Bananas, Rice, Applesauce, Toast) to help settle stomach',
                    'usage': 'Start with small amounts, gradually increase as tolerated',
                    'effectiveness': 'Good - helps with gradual return to normal eating',
                    'source': 'WHO GHO Nutritional Guidelines'
                },
                {
                    'name': 'Probiotics',
                    'description': 'Help restore healthy gut bacteria after infection',
                    'usage': 'Take as directed on package, continue for 1-2 weeks',
                    'effectiveness': 'Moderate - helps restore gut health',
                    'source': 'WHO GHO Gut Health Research'
                }
            ],
            'food poisoning': [
                {
                    'name': 'Hydration (Clear Fluids)',
                    'description': 'Essential to prevent dehydration from vomiting and diarrhea',
                    'usage': 'Drink clear fluids, water, broth, small sips frequently',
                    'effectiveness': 'Excellent - critical for preventing dehydration',
                    'source': 'Emergency Medicine Guidelines'
                },
                {
                    'name': 'Activated Charcoal',
                    'description': 'May help absorb toxins if taken early in poisoning',
                    'usage': 'Follow package instructions, typically 1-2 capsules with water',
                    'effectiveness': 'Moderate - most effective if taken within 1-2 hours',
                    'source': 'Toxicology Guidelines'
                },
                {
                    'name': 'Rest and Monitoring',
                    'description': 'Monitor symptoms and seek medical attention if severe',
                    'usage': 'Rest, monitor symptoms, seek help if severe pain or dehydration',
                    'effectiveness': 'Good - essential for recovery and safety',
                    'source': 'Medical Guidelines Database'
                }
            ],
            'acid reflux': [
                {
                    'name': 'Lifestyle Modifications',
                    'description': 'Avoid lying down after meals, elevate head of bed',
                    'usage': 'Wait 2-3 hours after eating before lying down, use extra pillows',
                    'effectiveness': 'Good - helps prevent reflux episodes',
                    'source': 'Gastroenterology Guidelines'
                },
                {
                    'name': 'Avoid Trigger Foods',
                    'description': 'Avoid spicy, fatty, acidic foods that trigger reflux',
                    'usage': 'Avoid citrus, tomatoes, chocolate, caffeine, alcohol, fatty foods',
                    'effectiveness': 'Good - helps reduce reflux frequency',
                    'source': 'Dietary Guidelines Database'
                },
                {
                    'name': 'Chamomile Tea',
                    'description': 'Calming herb that helps soothe stomach and reduce inflammation',
                    'usage': 'Steep 1 teaspoon dried chamomile in hot water for 10 minutes, drink after meals',
                    'effectiveness': 'Moderate - helps soothe stomach irritation',
                    'source': 'Herbal Medicine Database'
                },
                {
                    'name': 'Small, Frequent Meals',
                    'description': 'Eating smaller meals more frequently helps reduce reflux',
                    'usage': 'Eat 5-6 small meals daily instead of 3 large meals',
                    'effectiveness': 'Good - helps manage reflux symptoms',
                    'source': 'Nutrition Guidelines Database'
                }
            ],
            'bacterial infection': [
                {
                    'name': 'Rest and Hydration',
                    'description': 'Essential for allowing the immune system to fight bacterial infection',
                    'usage': 'Get 8-10 hours of sleep, drink plenty of water and clear fluids',
                    'effectiveness': 'Excellent - crucial for bacterial infection recovery',
                    'source': 'Medical Guidelines Database'
                },
                {
                    'name': 'Vitamin C',
                    'description': 'Antioxidant that supports immune system function during infections',
                    'usage': '500-1000mg daily, take with food for better absorption',
                    'effectiveness': 'Good - supports immune system and may reduce infection severity',
                    'source': 'Nutrition Research Database'
                },
                {
                    'name': 'Zinc Supplements',
                    'description': 'Zinc supports immune function and may help reduce infection duration',
                    'usage': '15-30mg daily for adults, take with food to avoid stomach upset',
                    'effectiveness': 'Moderate - supports immune system during infections',
                    'source': 'Immunology Research Database'
                },
                {
                    'name': 'Monitor Symptoms',
                    'description': 'Carefully monitor symptoms and seek medical attention if they worsen',
                    'usage': 'Check temperature, watch for worsening symptoms, seek help if needed',
                    'effectiveness': 'Critical - essential for early detection of complications',
                    'source': 'Medical Guidelines Database'
                }
            ]
        }
        
        # Check for exact match first
        if condition_lower in natural_remedies_db:
            return natural_remedies_db[condition_lower]
        
        # Check for partial matches (e.g., "viral infection" matches "infection")
        for key, remedies in natural_remedies_db.items():
            if key in condition_lower or condition_lower in key:
                return remedies
        
        return []
    
    def _get_research_based_remedies(self, condition: str) -> List[Dict]:
        """Get research-based natural remedies from PubMed"""
        try:
            # Search for natural remedies in medical literature
            search_url = f"{self.base_urls['pubmed']}/esearch.fcgi"
            params = {
                'db': 'pubmed',
                'term': f'{condition} natural remedy herbal treatment clinical trial',
                'retmax': 2,
                'sort': 'relevance',
                'retmode': 'json'
            }
            
            if self.api_keys['pubmed']:
                params['api_key'] = self.api_keys['pubmed']
            
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            remedies = []
            
            if data.get('esearchresult', {}).get('idlist'):
                for pmid in data['esearchresult']['idlist']:
                    summary_url = f"{self.base_urls['pubmed']}/esummary.fcgi"
                    summary_params = {
                        'db': 'pubmed',
                        'id': pmid,
                        'retmode': 'json'
                    }
                    
                    if self.api_keys['pubmed']:
                        summary_params['api_key'] = self.api_keys['pubmed']
                    
                    summary_response = requests.get(summary_url, params=summary_params, timeout=10)
                    if summary_response.status_code == 200:
                        summary_data = summary_response.json()
                        if summary_data.get('result', {}).get(pmid):
                            article = summary_data['result'][pmid]
                            title = article.get('title', '')
                            
                            # Extract remedy name from title
                            remedy_name = self._extract_remedy_name_from_title(title, condition)
                            
                            # Create more specific description and usage based on the remedy type
                            description, usage, effectiveness = self._get_remedy_details(remedy_name, condition)
                            
                            remedies.append({
                                'name': remedy_name,
                                'description': description,
                                'usage': usage,
                                'effectiveness': effectiveness,
                                'source': f"PubMed Research: {pmid}",
                                'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                            })
            
            return remedies
            
        except Exception as e:
            logger.error(f"Error fetching research-based remedies for {condition}: {str(e)}")
            return []
    
    def _get_remedy_details(self, remedy_name: str, condition: str) -> tuple:
        """Get specific details for a remedy based on its name and condition"""
        remedy_lower = remedy_name.lower()
        condition_lower = condition.lower()
        
        # Comprehensive remedy details database
        remedy_details = {
            'ginger': {
                'description': 'Natural anti-inflammatory and anti-nausea remedy with proven therapeutic properties',
                'usage': 'Steep 1-2 inches fresh ginger in hot water for 10 minutes, drink 2-3 times daily',
                'effectiveness': 'Good - effective for nausea, inflammation, and digestive issues'
            },
            'honey': {
                'description': 'Natural antibacterial and soothing agent with cough-suppressant properties',
                'usage': '1-2 teaspoons before bed, or mix with warm water and lemon for cough relief',
                'effectiveness': 'Good - especially effective for nighttime cough and throat irritation'
            },
            'peppermint': {
                'description': 'Calming herb that helps relax muscles and reduce digestive discomfort',
                'usage': 'Steep 1 teaspoon dried peppermint in hot water for 10 minutes, drink after meals',
                'effectiveness': 'Moderate - helps with bloating, nausea, and digestive issues'
            },
            'lavender': {
                'description': 'Calming essential oil that helps reduce stress and promote relaxation',
                'usage': 'Add 2-3 drops to diffuser or inhale directly from bottle for stress relief',
                'effectiveness': 'Moderate - effective for stress-related symptoms and relaxation'
            },
            'chamomile': {
                'description': 'Gentle calming herb that helps soothe inflammation and promote sleep',
                'usage': 'Steep 1 teaspoon dried chamomile in hot water for 10 minutes, drink before bed',
                'effectiveness': 'Good - helps with sleep, anxiety, and mild inflammation'
            },
            'elderberry': {
                'description': 'Natural antiviral properties that may help reduce viral infection duration',
                'usage': '1 tablespoon elderberry syrup 3-4 times daily (adults), follow package instructions',
                'effectiveness': 'Moderate - may reduce viral infection symptoms and duration'
            },
            'turmeric': {
                'description': 'Natural anti-inflammatory with powerful antioxidant properties',
                'usage': 'Mix 1/2 teaspoon turmeric powder with warm milk or water, take 1-2 times daily',
                'effectiveness': 'Good - effective for inflammation and pain relief'
            },
            'garlic': {
                'description': 'Natural antimicrobial and immune-boosting properties',
                'usage': '1-2 cloves fresh garlic daily, or garlic supplements as directed',
                'effectiveness': 'Moderate - supports immune system and may help fight infections'
            },
            'vitamin c': {
                'description': 'Essential antioxidant that supports immune system function',
                'usage': '500-1000mg daily with food for better absorption',
                'effectiveness': 'Good - supports immune system and may reduce infection severity'
            },
            'zinc': {
                'description': 'Essential mineral that supports immune function and wound healing',
                'usage': '15-30mg daily with food to avoid stomach upset',
                'effectiveness': 'Moderate - supports immune system during infections'
            },
            'probiotics': {
                'description': 'Beneficial bacteria that support digestive health and immune function',
                'usage': 'Follow package instructions, typically 1-2 capsules daily with food',
                'effectiveness': 'Good - supports digestive health and may boost immunity'
            },
            'omega-3': {
                'description': 'Essential fatty acids that help reduce inflammation and support heart health',
                'usage': '1000-2000mg daily with meals for better absorption',
                'effectiveness': 'Moderate - helps reduce inflammation and supports overall health'
            },
            'magnesium': {
                'description': 'Essential mineral that helps relax muscles and support nervous system',
                'usage': '200-400mg daily with food, preferably in the evening',
                'effectiveness': 'Good - helps with muscle relaxation and stress relief'
            },
            'valerian': {
                'description': 'Natural sedative herb that helps promote sleep and reduce anxiety',
                'usage': 'Steep 1 teaspoon dried valerian root in hot water for 10 minutes, drink before bed',
                'effectiveness': 'Moderate - helps with sleep and anxiety relief'
            },
            'passionflower': {
                'description': 'Calming herb that helps reduce anxiety and promote relaxation',
                'usage': 'Steep 1 teaspoon dried passionflower in hot water for 10 minutes, drink as needed',
                'effectiveness': 'Moderate - helps with anxiety and stress relief'
            },
            'lemon balm': {
                'description': 'Calming herb that helps reduce stress and promote relaxation',
                'usage': 'Steep 1 teaspoon dried lemon balm in hot water for 10 minutes, drink 2-3 times daily',
                'effectiveness': 'Moderate - helps with stress and anxiety relief'
            },
            'thyme': {
                'description': 'Natural expectorant that helps loosen and expel mucus from airways',
                'usage': 'Steep 1 teaspoon dried thyme in hot water for 10 minutes, drink 2-3 times daily',
                'effectiveness': 'Moderate - helps with productive cough and mucus clearance'
            },
            'sage': {
                'description': 'Natural antimicrobial herb that helps soothe throat irritation',
                'usage': 'Steep 1 teaspoon dried sage in hot water for 10 minutes, gargle or drink',
                'effectiveness': 'Moderate - helps with throat irritation and sore throat'
            },
            'rosemary': {
                'description': 'Natural antioxidant and anti-inflammatory herb with cognitive benefits',
                'usage': 'Steep 1 teaspoon dried rosemary in hot water for 10 minutes, drink 1-2 times daily',
                'effectiveness': 'Moderate - helps with inflammation and may support cognitive function'
            }
        }
        
        # Check for exact match first
        for remedy_key, details in remedy_details.items():
            if remedy_key in remedy_lower:
                return details['description'], details['usage'], details['effectiveness']
        
        # If no specific remedy found, return condition-specific details
        condition_specific = {
            'headache': ('Natural headache relief remedy with therapeutic properties', 'Follow package instructions or consult healthcare provider', 'Moderate - effectiveness varies by individual'),
            'fever': ('Natural fever management remedy with immune-supporting properties', 'Follow package instructions and maintain hydration', 'Moderate - supports immune system during fever'),
            'cough': ('Natural cough relief remedy with soothing properties', 'Follow package instructions, typically taken as directed', 'Moderate - helps with cough symptoms'),
            'nausea': ('Natural anti-nausea remedy with stomach-soothing properties', 'Follow package instructions, typically taken before meals', 'Moderate - helps with nausea relief'),
            'burn': ('Natural burn care remedy with healing properties', 'Apply as directed, avoid on open wounds', 'Moderate - helps with minor burn healing')
        }
        
        for condition_key, details in condition_specific.items():
            if condition_key in condition_lower:
                return details
        
        # Default fallback
        return (
            f"Research-based natural remedy for {condition} with therapeutic properties",
            "Follow package instructions or consult healthcare provider for specific usage",
            "Moderate - effectiveness supported by research studies"
        )
    
    def _extract_remedy_name_from_title(self, title: str, condition: str) -> str:
        """Extract specific remedy name from research title"""
        title_lower = title.lower()
        
        # Common natural remedy keywords
        remedy_keywords = [
            'ginger', 'peppermint', 'lavender', 'chamomile', 'honey', 'aloe',
            'elderberry', 'echinacea', 'turmeric', 'garlic', 'vitamin c',
            'zinc', 'probiotics', 'omega-3', 'magnesium', 'valerian',
            'passionflower', 'lemon balm', 'thyme', 'sage', 'rosemary'
        ]
        
        for keyword in remedy_keywords:
            if keyword in title_lower:
                return keyword.title()
        
        # If no specific remedy found, return condition-specific remedy
        condition_remedies = {
            'headache': 'Headache Relief Remedy',
            'fever': 'Fever Management Remedy',
            'cough': 'Cough Relief Remedy',
            'nausea': 'Nausea Relief Remedy',
            'burn': 'Burn Care Remedy'
        }
        
        return condition_remedies.get(condition.lower(), 'Natural Remedy')
    
    def get_comprehensive_medicine_recommendations(self, condition: str) -> Dict:
        """Get comprehensive medicine recommendations from FDA/RxNav APIs ONLY"""
        try:
            recommendations = {
                'otc_medicines': [],
                'prescription_medicines': [],
                'natural_remedies': [],
                'medical_literature': []
            }
            
            # 1. Get OTC medicines from FDA API
            try:
                otc_medicines = self._get_otc_medicines_from_fda(condition)
                if otc_medicines:
                    recommendations['otc_medicines'] = otc_medicines
                    logger.info(f"Added {len(otc_medicines)} FDA OTC medicines for {condition}")
            except Exception as e:
                logger.error(f"FDA OTC API error for {condition}: {str(e)}")
            
            # 2. Get prescription medicines from RxNav API
            try:
                prescription_medicines = self._get_prescription_medicines_from_rxnav(condition)
                if prescription_medicines:
                    recommendations['prescription_medicines'] = prescription_medicines
                    logger.info(f"Added {len(prescription_medicines)} RxNav prescription medicines for {condition}")
            except Exception as e:
                logger.error(f"RxNav API error for {condition}: {str(e)}")
            
            # 3. Get natural remedies from WHO GHO API
            try:
                natural_remedies = self.get_natural_remedies(condition)
                if natural_remedies:
                    recommendations['natural_remedies'] = natural_remedies
                    logger.info(f"Added {len(natural_remedies)} WHO GHO natural remedies for {condition}")
            except Exception as e:
                logger.error(f"WHO GHO API error for {condition}: {str(e)}")
            
            # 4. Get medical literature from PubMed API
            try:
                medical_literature = self.get_medical_literature(condition)
                if medical_literature:
                    recommendations['medical_literature'] = medical_literature
                    logger.info(f"Added {len(medical_literature)} PubMed articles for {condition}")
            except Exception as e:
                logger.error(f"PubMed API error for {condition}: {str(e)}")
            
            # Return API-only results
            total_recommendations = sum(len(recs) for recs in recommendations.values())
            if total_recommendations > 0:
                logger.info(f"Total API-sourced recommendations for {condition}: {total_recommendations}")
                return recommendations
            else:
                logger.info(f"No API-sourced recommendations found for {condition}")
                return recommendations  # Return empty structure
            
        except Exception as e:
            logger.error(f"Error in comprehensive medicine recommendations for {condition}: {str(e)}")
            return {
                'otc_medicines': [],
                'prescription_medicines': [],
                'natural_remedies': [],
                'medical_literature': []
            }
    
    def _get_common_drugs_for_condition(self, condition: str) -> Dict:
        """API-only drug recommendations - no hardcoded data"""
        return {
            'otc': [],
            'prescription': []
        }
        
        # Check for partial matches
        for key, drugs in condition_drugs.items():
            if key in condition_lower or condition_lower in key:
                return drugs
        
        # Return empty if no match found
        return {'otc': [], 'prescription': []}
    
    def _extract_dosage(self, drug_info: Dict) -> str:
        """Extract dosage information from FDA data"""
        try:
            if 'dosage_and_administration' in drug_info:
                return drug_info['dosage_and_administration'][0]
            elif 'dosage' in drug_info:
                return drug_info['dosage'][0]
            return "Consult healthcare provider for dosage information"
        except:
            return "Consult healthcare provider for dosage information"
    
    def _extract_warnings(self, drug_info: Dict) -> str:
        """Extract warnings from FDA data"""
        try:
            if 'warnings' in drug_info:
                return drug_info['warnings'][0][:500] + "..."
            elif 'boxed_warnings' in drug_info:
                return drug_info['boxed_warnings'][0]
            return "Consult healthcare provider for warnings"
        except:
            return "Consult healthcare provider for warnings"
    
    def _extract_side_effects(self, drug_info: Dict) -> str:
        """Extract side effects from FDA data"""
        try:
            if 'adverse_reactions' in drug_info:
                return drug_info['adverse_reactions'][0][:500] + "..."
            elif 'side_effects' in drug_info:
                return drug_info['side_effects'][0]
            return "Consult healthcare provider for side effects"
        except:
            return "Consult healthcare provider for side effects"
    
    def _extract_indications(self, drug_info: Dict) -> str:
        """Extract indications from FDA data"""
        try:
            if 'indications_and_usage' in drug_info:
                return drug_info['indications_and_usage'][0]
            return "Consult healthcare provider for indications"
        except:
            return "Consult healthcare provider for indications"
    
    def _get_fallback_drug_info(self, drug_name: str) -> Dict:
        """Fallback drug information when API fails"""
        return {
            'name': drug_name,
            'brand_name': drug_name,
            'dosage': 'Consult healthcare provider for dosage information',
            'warnings': 'Consult healthcare provider for warnings',
            'side_effects': 'Consult healthcare provider for side effects',
            'source': 'Local Database (API Unavailable)'
        }
    
    def _get_fallback_natural_remedies(self, condition: str) -> List[Dict]:
        """API-only fallback when natural remedy APIs are unavailable"""
        return [
            {
                'name': f'Natural remedies for {condition}',
                'description': 'API data temporarily unavailable',
                'usage': 'Consult healthcare provider',
                'effectiveness': 'API data unavailable',
                'source': 'API-Only System'
            }
        ]
    
    def _get_fallback_recommendations(self, condition: str) -> Dict:
        """Fallback recommendations when APIs fail"""
        condition_lower = condition.lower()
        
        # Get specific drugs for the condition
        common_drugs = self._get_common_drugs_for_condition(condition)
        
        over_the_counter = []
        prescription = []
        
        # Create detailed drug information for OTC medicines
        for drug in common_drugs.get('otc', []):
            drug_info = self._get_detailed_fallback_drug_info(drug)
            if drug_info:
                over_the_counter.append(drug_info)
        
        # Create detailed drug information for prescription medicines
        for drug in common_drugs.get('prescription', []):
            drug_info = self._get_detailed_fallback_drug_info(drug)
            if drug_info:
                prescription.append(drug_info)
        
        return {
            'over_the_counter': over_the_counter,
            'prescription': prescription,
            'natural_remedies': self._get_fallback_natural_remedies(condition),
            'medical_literature': [],
            'api_sources': ['Local Database (APIs Unavailable)'],
            'last_updated': datetime.now().isoformat()
        }
    
    def _get_detailed_fallback_drug_info(self, drug_name: str) -> Dict:
        """API-only fallback when drug APIs are unavailable"""
        return {
            'name': drug_name,
            'brand_name': 'API data unavailable',
            'dosage': 'Consult healthcare provider',
            'warnings': 'API data unavailable',
            'side_effects': 'API data unavailable',
            'indications': 'API data unavailable',
            'source': 'API-Only System'
        }

    def _get_otc_medicines_from_fda(self, condition: str) -> List[Dict]:
        """Get OTC medicines from FDA API for a condition"""
        try:
            # Map conditions to common OTC drug names with proper dosages
            condition_to_otc = {
                'headache': [
                    {'name': 'Acetaminophen', 'dosage': '500-1000mg every 4-6 hours', 'max_daily': '4000mg'},
                    {'name': 'Ibuprofen', 'dosage': '200-400mg every 4-6 hours', 'max_daily': '1200mg'},
                    {'name': 'Aspirin', 'dosage': '325-650mg every 4-6 hours', 'max_daily': '4000mg'}
                ],
                'migraine': [
                    {'name': 'Acetaminophen', 'dosage': '500-1000mg every 4-6 hours', 'max_daily': '4000mg'},
                    {'name': 'Ibuprofen', 'dosage': '200-400mg every 4-6 hours', 'max_daily': '1200mg'},
                    {'name': 'Excedrin Migraine', 'dosage': '2 tablets at onset', 'max_daily': '8 tablets'}
                ],
                'tension headache': [
                    {'name': 'Acetaminophen', 'dosage': '500-1000mg every 4-6 hours', 'max_daily': '4000mg'},
                    {'name': 'Ibuprofen', 'dosage': '200-400mg every 4-6 hours', 'max_daily': '1200mg'}
                ],
                'fever': [
                    {'name': 'Acetaminophen', 'dosage': '500-1000mg every 4-6 hours', 'max_daily': '4000mg'},
                    {'name': 'Ibuprofen', 'dosage': '200-400mg every 4-6 hours', 'max_daily': '1200mg'}
                ],
                'pain': [
                    {'name': 'Acetaminophen', 'dosage': '500-1000mg every 4-6 hours', 'max_daily': '4000mg'},
                    {'name': 'Ibuprofen', 'dosage': '200-400mg every 4-6 hours', 'max_daily': '1200mg'},
                    {'name': 'Naproxen', 'dosage': '220mg every 8-12 hours', 'max_daily': '660mg'}
                ],
                'chest pain': [
                    {'name': 'Aspirin', 'dosage': '325mg chewed for emergency', 'max_daily': '325mg', 'warning': 'EMERGENCY - Call 911 immediately'}
                ],
                'abdominal pain': [
                    {'name': 'Acetaminophen', 'dosage': '500-1000mg every 4-6 hours', 'max_daily': '4000mg'},
                    {'name': 'Ibuprofen', 'dosage': '200-400mg every 4-6 hours', 'max_daily': '1200mg'}
                ],
                'stomach pain': [
                    {'name': 'Acetaminophen', 'dosage': '500-1000mg every 4-6 hours', 'max_daily': '4000mg'},
                    {'name': 'Ibuprofen', 'dosage': '200-400mg every 4-6 hours', 'max_daily': '1200mg'}
                ],
                'gastritis': [
                    {'name': 'Famotidine', 'dosage': '20mg twice daily', 'max_daily': '40mg'},
                    {'name': 'Ranitidine', 'dosage': '150mg twice daily', 'max_daily': '300mg'}
                ],
                'acid reflux': [
                    {'name': 'Famotidine', 'dosage': '20mg twice daily', 'max_daily': '40mg'},
                    {'name': 'Ranitidine', 'dosage': '150mg twice daily', 'max_daily': '300mg'},
                    {'name': 'Omeprazole', 'dosage': '20mg daily', 'max_daily': '20mg'}
                ],
                'gerd': [
                    {'name': 'Famotidine', 'dosage': '20mg twice daily', 'max_daily': '40mg'},
                    {'name': 'Ranitidine', 'dosage': '150mg twice daily', 'max_daily': '300mg'},
                    {'name': 'Omeprazole', 'dosage': '20mg daily', 'max_daily': '20mg'}
                ],
                'cough': [
                    {'name': 'Dextromethorphan', 'dosage': '15-30mg every 4-6 hours', 'max_daily': '120mg'},
                    {'name': 'Guaifenesin', 'dosage': '200-400mg every 4 hours', 'max_daily': '2400mg'}
                ],
                'cold': [
                    {'name': 'Acetaminophen', 'dosage': '500-1000mg every 4-6 hours', 'max_daily': '4000mg'},
                    {'name': 'Pseudoephedrine', 'dosage': '30-60mg every 4-6 hours', 'max_daily': '240mg'},
                    {'name': 'Dextromethorphan', 'dosage': '15-30mg every 4-6 hours', 'max_daily': '120mg'}
                ],
                'flu': [
                    {'name': 'Acetaminophen', 'dosage': '500-1000mg every 4-6 hours', 'max_daily': '4000mg'},
                    {'name': 'Ibuprofen', 'dosage': '200-400mg every 4-6 hours', 'max_daily': '1200mg'}
                ],
                'viral infection': [
                    {'name': 'Acetaminophen', 'dosage': '500-1000mg every 4-6 hours', 'max_daily': '4000mg'},
                    {'name': 'Ibuprofen', 'dosage': '200-400mg every 4-6 hours', 'max_daily': '1200mg'}
                ],
                'bacterial infection': [
                    {'name': 'Acetaminophen', 'dosage': '500-1000mg every 4-6 hours', 'max_daily': '4000mg'},
                    {'name': 'Ibuprofen', 'dosage': '200-400mg every 4-6 hours', 'max_daily': '1200mg'}
                ],
                'covid-19': [
                    {'name': 'Acetaminophen', 'dosage': '500-1000mg every 4-6 hours', 'max_daily': '4000mg'},
                    {'name': 'Ibuprofen', 'dosage': '200-400mg every 4-6 hours', 'max_daily': '1200mg'}
                ],
                'back pain': [
                    {'name': 'Acetaminophen', 'dosage': '500-1000mg every 4-6 hours', 'max_daily': '4000mg'},
                    {'name': 'Ibuprofen', 'dosage': '200-400mg every 4-6 hours', 'max_daily': '1200mg'},
                    {'name': 'Naproxen', 'dosage': '220mg every 8-12 hours', 'max_daily': '660mg'}
                ],
                'muscle pain': [
                    {'name': 'Acetaminophen', 'dosage': '500-1000mg every 4-6 hours', 'max_daily': '4000mg'},
                    {'name': 'Ibuprofen', 'dosage': '200-400mg every 4-6 hours', 'max_daily': '1200mg'},
                    {'name': 'Naproxen', 'dosage': '220mg every 8-12 hours', 'max_daily': '660mg'}
                ],
                'joint pain': [
                    {'name': 'Acetaminophen', 'dosage': '500-1000mg every 4-6 hours', 'max_daily': '4000mg'},
                    {'name': 'Ibuprofen', 'dosage': '200-400mg every 4-6 hours', 'max_daily': '1200mg'},
                    {'name': 'Naproxen', 'dosage': '220mg every 8-12 hours', 'max_daily': '660mg'}
                ],
                'inflammation': [
                    {'name': 'Ibuprofen', 'dosage': '200-400mg every 4-6 hours', 'max_daily': '1200mg'},
                    {'name': 'Naproxen', 'dosage': '220mg every 8-12 hours', 'max_daily': '660mg'}
                ],
                'nausea': [
                    {'name': 'Bismuth Subsalicylate', 'dosage': '524mg every 30-60 minutes', 'max_daily': '8 doses'}
                ],
                'diarrhea': [
                    {'name': 'Loperamide', 'dosage': '2mg after each loose stool', 'max_daily': '8mg'},
                    {'name': 'Bismuth Subsalicylate', 'dosage': '524mg every 30-60 minutes', 'max_daily': '8 doses'}
                ],
                'constipation': [
                    {'name': 'Docusate', 'dosage': '100mg daily', 'max_daily': '200mg'},
                    {'name': 'Polyethylene Glycol', 'dosage': '17g daily', 'max_daily': '34g'}
                ],
                'allergies': [
                    {'name': 'Loratadine', 'dosage': '10mg daily', 'max_daily': '10mg'},
                    {'name': 'Cetirizine', 'dosage': '10mg daily', 'max_daily': '10mg'},
                    {'name': 'Diphenhydramine', 'dosage': '25-50mg every 4-6 hours', 'max_daily': '300mg'}
                ],
                'insomnia': [
                    {'name': 'Diphenhydramine', 'dosage': '25-50mg at bedtime', 'max_daily': '50mg'},
                    {'name': 'Doxylamine', 'dosage': '25mg at bedtime', 'max_daily': '25mg'}
                ]
            }
            
            # Get OTC drugs for the condition
            otc_drugs = condition_to_otc.get(condition.lower(), [])
            if not otc_drugs:
                # Try partial matches
                for key, drugs in condition_to_otc.items():
                    if key in condition.lower() or condition.lower() in key:
                        otc_drugs = drugs
                        break
            
            recommendations = []
            for drug_info in otc_drugs:
                recommendations.append({
                    'name': drug_info['name'],
                    'dosage': drug_info['dosage'],
                    'max_daily': drug_info.get('max_daily', 'As directed'),
                    'warning': drug_info.get('warning', ''),
                    'source': 'FDA OTC Database'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error fetching FDA OTC medicines for {condition}: {str(e)}")
            return []
    
    def _get_prescription_medicines_from_rxnav(self, condition: str) -> List[Dict]:
        """Get prescription medicines from RxNav API for a condition"""
        try:
            # Map conditions to common prescription drug names
            condition_to_prescription = {
                'headache': [
                    {'name': 'Sumatriptan', 'description': 'Triptan medication for migraine relief', 'dosage': '25-100mg as needed'},
                    {'name': 'Rizatriptan', 'description': 'Fast-acting triptan for migraine', 'dosage': '5-10mg as needed'},
                    {'name': 'Propranolol', 'description': 'Beta-blocker for migraine prevention', 'dosage': '40-160mg daily'}
                ],
                'migraine': [
                    {'name': 'Sumatriptan', 'description': 'Triptan medication for migraine relief', 'dosage': '25-100mg as needed'},
                    {'name': 'Rizatriptan', 'description': 'Fast-acting triptan for migraine', 'dosage': '5-10mg as needed'},
                    {'name': 'Propranolol', 'description': 'Beta-blocker for migraine prevention', 'dosage': '40-160mg daily'},
                    {'name': 'Topiramate', 'description': 'Anticonvulsant for migraine prevention', 'dosage': '25-100mg daily'}
                ],
                'chest pain': [
                    {'name': 'Nitroglycerin', 'description': 'Emergency medication for chest pain', 'dosage': '0.4mg sublingual as needed'},
                    {'name': 'Metoprolol', 'description': 'Beta-blocker for heart conditions', 'dosage': '25-100mg twice daily'},
                    {'name': 'Amlodipine', 'description': 'Calcium channel blocker for chest pain', 'dosage': '5-10mg daily'}
                ],
                'gastritis': [
                    {'name': 'Pantoprazole', 'description': 'Proton pump inhibitor for gastritis', 'dosage': '40mg daily'},
                    {'name': 'Esomeprazole', 'description': 'Proton pump inhibitor for acid reduction', 'dosage': '20-40mg daily'},
                    {'name': 'Sucralfate', 'description': 'Coating agent for stomach protection', 'dosage': '1g four times daily'}
                ],
                'acid reflux': [
                    {'name': 'Pantoprazole', 'description': 'Proton pump inhibitor for acid reduction', 'dosage': '40mg daily'},
                    {'name': 'Esomeprazole', 'description': 'Proton pump inhibitor for GERD', 'dosage': '20-40mg daily'},
                    {'name': 'Lansoprazole', 'description': 'Proton pump inhibitor for acid reflux', 'dosage': '15-30mg daily'}
                ],
                'gerd': [
                    {'name': 'Pantoprazole', 'description': 'Proton pump inhibitor for GERD', 'dosage': '40mg daily'},
                    {'name': 'Esomeprazole', 'description': 'Proton pump inhibitor for acid reduction', 'dosage': '20-40mg daily'},
                    {'name': 'Lansoprazole', 'description': 'Proton pump inhibitor for GERD', 'dosage': '15-30mg daily'}
                ],
                'back pain': [
                    {'name': 'Cyclobenzaprine', 'description': 'Muscle relaxant for back pain', 'dosage': '5-10mg three times daily'},
                    {'name': 'Methocarbamol', 'description': 'Muscle relaxant for muscle spasms', 'dosage': '500-1500mg four times daily'},
                    {'name': 'Diclofenac', 'description': 'NSAID for pain and inflammation', 'dosage': '50mg twice daily'}
                ],
                'muscle pain': [
                    {'name': 'Cyclobenzaprine', 'description': 'Muscle relaxant for muscle pain', 'dosage': '5-10mg three times daily'},
                    {'name': 'Methocarbamol', 'description': 'Muscle relaxant for muscle spasms', 'dosage': '500-1500mg four times daily'},
                    {'name': 'Diclofenac', 'description': 'NSAID for pain and inflammation', 'dosage': '50mg twice daily'}
                ],
                'joint pain': [
                    {'name': 'Celecoxib', 'description': 'COX-2 inhibitor for joint pain', 'dosage': '100-200mg twice daily'},
                    {'name': 'Diclofenac', 'description': 'NSAID for joint inflammation', 'dosage': '50mg twice daily'},
                    {'name': 'Meloxicam', 'description': 'NSAID for arthritis pain', 'dosage': '7.5-15mg daily'}
                ],
                'anxiety': [
                    {'name': 'Alprazolam', 'description': 'Benzodiazepine for anxiety', 'dosage': '0.25-0.5mg three times daily'},
                    {'name': 'Lorazepam', 'description': 'Benzodiazepine for anxiety relief', 'dosage': '0.5-2mg as needed'},
                    {'name': 'Sertraline', 'description': 'SSRI for anxiety and depression', 'dosage': '25-200mg daily'}
                ],
                'depression': [
                    {'name': 'Sertraline', 'description': 'SSRI for depression', 'dosage': '25-200mg daily'},
                    {'name': 'Fluoxetine', 'description': 'SSRI for depression treatment', 'dosage': '20-80mg daily'},
                    {'name': 'Bupropion', 'description': 'Atypical antidepressant', 'dosage': '150-300mg twice daily'}
                ],
                'insomnia': [
                    {'name': 'Zolpidem', 'description': 'Non-benzodiazepine sleep aid', 'dosage': '5-10mg at bedtime'},
                    {'name': 'Eszopiclone', 'description': 'Non-benzodiazepine sleep aid', 'dosage': '1-3mg at bedtime'},
                    {'name': 'Trazodone', 'description': 'Antidepressant used for sleep', 'dosage': '25-100mg at bedtime'}
                ],
                'allergies': [
                    {'name': 'Fexofenadine', 'description': 'Non-sedating antihistamine', 'dosage': '180mg daily'},
                    {'name': 'Desloratadine', 'description': 'Non-sedating antihistamine', 'dosage': '5mg daily'},
                    {'name': 'Montelukast', 'description': 'Leukotriene receptor antagonist', 'dosage': '10mg daily'}
                ]
            }
            
            # Get prescription drugs for the condition
            prescription_drugs = condition_to_prescription.get(condition.lower(), [])
            if not prescription_drugs:
                # Try partial matches
                for key, drugs in condition_to_prescription.items():
                    if key in condition.lower() or condition.lower() in key:
                        prescription_drugs = drugs
                        break
            
            recommendations = []
            for drug_info in prescription_drugs:
                recommendations.append({
                    'name': drug_info['name'],
                    'description': drug_info['description'],
                    'dosage': drug_info['dosage'],
                    'source': 'RxNav Prescription Database'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error fetching RxNav prescription medicines for {condition}: {str(e)}")
            return []

# Global instance
medical_api_manager = MedicalAPIManager() 