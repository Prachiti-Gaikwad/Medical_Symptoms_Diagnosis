import requests
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class WHOGHOAPI:
    """WHO GHO (Global Health Observatory) API integration - FREE & OPEN SOURCE"""
    
    def __init__(self):
        self.base_url = Config.WHO_GHO_BASE_URL
        self.timeout = 15
        
    def is_available(self) -> bool:
        """Check if WHO GHO API is available (always true - it's free!)"""
        return True
    
    def get_health_indicators(self, condition: str) -> List[Dict]:
        """Get health indicators from WHO GHO API"""
        try:
            # Search for health indicators related to the condition
            url = f"{self.base_url}/Indicator"
            
            # Use simpler OData filtering - just get all indicators first
            params = {
                '$format': 'json',
                '$top': 100
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            indicators = []
            
            if data.get('value'):
                for item in data['value']:
                    indicator_name = item.get('IndicatorName', '').lower()
                    if condition.lower() in indicator_name:
                        indicator = self._parse_health_indicator(item, condition)
                        if indicator:
                            indicators.append(indicator)
            
            logger.info(f"Retrieved {len(indicators)} WHO GHO indicators for {condition}")
            return indicators
            
        except requests.exceptions.RequestException as e:
            logger.error(f"WHO GHO API request failed: {str(e)}")
            return self._get_fallback_health_data(condition)
        except Exception as e:
            logger.error(f"Error processing WHO GHO data: {str(e)}")
            return self._get_fallback_health_data(condition)
    
    def get_traditional_medicine_data(self, condition: str) -> List[Dict]:
        """Get traditional medicine data from WHO GHO"""
        try:
            # Search for traditional medicine indicators
            url = f"{self.base_url}/Indicator"
            
            # Get all indicators and filter locally
            params = {
                '$format': 'json',
                '$top': 200
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            all_remedies = []
            
            if data.get('value'):
                for item in data['value']:
                    indicator_name = item.get('IndicatorName', '').lower()
                    
                    # Look for traditional medicine related indicators
                    traditional_keywords = ['traditional', 'herbal', 'medicine', 'remedy', 'natural']
                    condition_match = condition.lower() in indicator_name
                    
                    for keyword in traditional_keywords:
                        if keyword in indicator_name and condition_match:
                            remedy = self._parse_traditional_remedy(item, condition)
                            if remedy:
                                all_remedies.append(remedy)
                                break  # Avoid duplicates
            
            # If no WHO GHO data found, provide enhanced fallback remedies
            if not all_remedies:
                all_remedies = self._get_enhanced_fallback_traditional_remedies(condition)
            
            return all_remedies
            
        except Exception as e:
            logger.error(f"Error fetching WHO traditional medicine data: {str(e)}")
            return self._get_enhanced_fallback_traditional_remedies(condition)
    
    def get_global_health_practices(self, condition: str) -> List[Dict]:
        """Get global health practices from WHO GHO"""
        try:
            url = f"{self.base_url}/Indicator"
            
            # Get all indicators and filter locally
            params = {
                '$format': 'json',
                '$top': 200
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            practices = []
            
            if data.get('value'):
                for item in data['value']:
                    indicator_name = item.get('IndicatorName', '').lower()
                    
                    # Look for health practices and treatments
                    practice_keywords = ['treatment', 'practice', 'care', 'health']
                    condition_match = condition.lower() in indicator_name
                    
                    for keyword in practice_keywords:
                        if keyword in indicator_name and condition_match:
                            practice = self._parse_health_practice(item, condition)
                            if practice:
                                practices.append(practice)
                                break  # Avoid duplicates
            
            return practices
            
        except Exception as e:
            logger.error(f"Error fetching WHO health practices: {str(e)}")
            return []
    
    def get_herbal_medicine_indicators(self, herb_name: str) -> Dict:
        """Get herbal medicine indicators from WHO GHO"""
        try:
            url = f"{self.base_url}/Indicator"
            
            # Get all indicators and filter locally
            params = {
                '$format': 'json',
                '$top': 200
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('value'):
                for item in data['value']:
                    indicator_name = item.get('IndicatorName', '').lower()
                    if herb_name.lower() in indicator_name:
                        return self._parse_herbal_indicator(item, herb_name)
            
            return {}
            
        except Exception as e:
            logger.error(f"Error fetching WHO herbal medicine data: {str(e)}")
            return {}
    
    def _parse_health_indicator(self, item: Dict, condition: str) -> Optional[Dict]:
        """Parse WHO GHO health indicator data"""
        try:
            indicator_name = item.get('IndicatorName', '')
            value = item.get('Value', '')
            location = item.get('Location', 'Unknown')
            time_dim = item.get('TimeDim', '')
            comments = item.get('Comments', '')
            
            return {
                'name': indicator_name,
                'description': comments or f"WHO GHO health indicator for {condition}",
                'usage': f"Global health data from {location}",
                'effectiveness': self._assess_effectiveness(value),
                'source': f"WHO GHO Database - {location}",
                'region': location,
                'year': time_dim,
                'who_data': value,
                'type': 'who_gho_indicator'
            }
            
        except Exception as e:
            logger.error(f"Error parsing WHO GHO indicator: {str(e)}")
            return None
    
    def _parse_traditional_remedy(self, item: Dict, condition: str) -> Optional[Dict]:
        """Parse WHO GHO traditional remedy data"""
        try:
            indicator_name = item.get('IndicatorName', '')
            value = item.get('Value', '')
            location = item.get('Location', 'Unknown')
            comments = item.get('Comments', '')
            
            remedy_name = self._extract_remedy_name(indicator_name, condition)
            
            if remedy_name:
                return {
                    'name': remedy_name,
                    'description': comments or f"Traditional medicine practice from {location}",
                    'usage': f"Traditional remedy for {condition}",
                    'effectiveness': self._assess_effectiveness(value),
                    'source': f"WHO GHO Traditional Medicine - {location}",
                    'region': location,
                    'who_data': value,
                    'type': 'who_traditional'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing WHO traditional remedy: {str(e)}")
            return None
    
    def _parse_health_practice(self, item: Dict, condition: str) -> Optional[Dict]:
        """Parse WHO GHO health practice data"""
        try:
            indicator_name = item.get('IndicatorName', '')
            value = item.get('Value', '')
            location = item.get('Location', 'Unknown')
            comments = item.get('Comments', '')
            
            return {
                'name': indicator_name,
                'description': comments or f"Health practice from {location}",
                'usage': f"Global health practice for {condition}",
                'effectiveness': self._assess_effectiveness(value),
                'source': f"WHO GHO Health Practices - {location}",
                'region': location,
                'practice_data': value,
                'type': 'who_practice'
            }
            
        except Exception as e:
            logger.error(f"Error parsing WHO health practice: {str(e)}")
            return None
    
    def _parse_herbal_indicator(self, item: Dict, herb_name: str) -> Dict:
        """Parse WHO GHO herbal medicine indicator"""
        try:
            indicator_name = item.get('IndicatorName', '')
            value = item.get('Value', '')
            location = item.get('Location', 'Unknown')
            comments = item.get('Comments', '')
            
            return {
                'name': herb_name,
                'description': comments or f"Herbal medicine data from WHO GHO",
                'usage': f"Traditional herbal medicine",
                'effectiveness': self._assess_effectiveness(value),
                'source': f"WHO GHO Herbal Medicine - {location}",
                'region': location,
                'herbal_data': value,
                'type': 'who_herbal'
            }
            
        except Exception as e:
            logger.error(f"Error parsing WHO herbal indicator: {str(e)}")
            return {}
    
    def _extract_remedy_name(self, indicator_name: str, condition: str) -> Optional[str]:
        """Extract remedy name from WHO GHO indicator"""
        try:
            # Common traditional medicine keywords
            keywords = [
                'traditional medicine', 'herbal', 'natural remedy', 
                'medicinal plant', 'folk medicine', 'indigenous medicine'
            ]
            
            for keyword in keywords:
                if keyword.lower() in indicator_name.lower():
                    # Extract the specific remedy name
                    parts = indicator_name.split()
                    for i, part in enumerate(parts):
                        if part.lower() in ['medicine', 'remedy', 'herbal']:
                            if i > 0:
                                return ' '.join(parts[:i])
                    return indicator_name.split('-')[0].strip()
            
            return None
            
        except Exception:
            return None
    
    def _assess_effectiveness(self, value: str) -> str:
        """Assess effectiveness based on WHO GHO data value"""
        try:
            # Convert value to numeric if possible
            if isinstance(value, (int, float)):
                if value > 80:
                    return "High effectiveness based on WHO GHO data"
                elif value > 60:
                    return "Moderate effectiveness based on WHO GHO data"
                elif value > 40:
                    return "Some effectiveness based on WHO GHO data"
                else:
                    return "Limited effectiveness based on WHO GHO data"
            else:
                return "Effectiveness data available from WHO GHO"
                
        except Exception:
            return "Effectiveness data available from WHO GHO"
    
    def _get_fallback_health_data(self, condition: str) -> List[Dict]:
        """API-only fallback when WHO GHO API is unavailable"""
        return [
            {
                'name': f'WHO GHO Health Data for {condition}',
                'description': 'WHO GHO API temporarily unavailable',
                'usage': 'Consult healthcare provider',
                'effectiveness': 'API data unavailable',
                'source': 'API-Only System',
                'region': 'Global',
                'type': 'api_only_fallback'
            }
        ]
    
    def _get_enhanced_fallback_traditional_remedies(self, condition: str) -> List[Dict]:
        """API-only fallback when WHO GHO API is unavailable"""
        return [
            {
                'name': f'Traditional remedies for {condition}',
                'description': 'WHO GHO API temporarily unavailable',
                'usage': 'Consult healthcare provider',
                'effectiveness': 'API data unavailable',
                'source': 'API-Only System',
                'region': 'Global',
                'type': 'api_only_fallback'
            }
        ]
        # API-Only System - No hardcoded data
        return []
    
    def get_api_status(self) -> Dict:
        """Get WHO GHO API status and information"""
        return {
            'available': self.is_available(),
            'api_key_required': False,
            'base_url': self.base_url,
            'timeout': self.timeout,
            'description': 'WHO GHO (Global Health Observatory) API - FREE & OPEN SOURCE',
            'source': 'https://ghoapi.azureedge.net/api/'
        } 