from flask import Blueprint, request, jsonify, render_template
from app.utils import analyze_symptoms, validate_symptoms_input, detect_language, translate_analysis_results
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@main_bp.route('/analyze', methods=['POST'])
def analyze():
    """Analyze symptoms and return potential diagnoses"""
    try:
        data = request.get_json()
        if not data or 'symptoms' not in data:
            return jsonify({
                'success': False,
                'error': 'Symptoms data is required'
            }), 400
        
        symptoms = data['symptoms']
        target_language = data.get('language', 'en')  # Default to English
        
        # Validate input
        is_valid, error_message = validate_symptoms_input(symptoms)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_message
            }), 400
        
        # Detect language if not specified
        detected_language = detect_language(symptoms)
        
        # Analyze symptoms
        try:
            result = analyze_symptoms(symptoms)
            
            # Validate result
            if not result or not isinstance(result, dict):
                logger.error("Analysis returned invalid result")
                return jsonify({
                    'success': False,
                    'error': 'Analysis failed to return valid results. Please try again.'
                }), 500
            
            # Ensure required fields exist
            if 'potential_diagnoses' not in result:
                result['potential_diagnoses'] = []
            if 'recommendations' not in result:
                result['recommendations'] = []
            if 'warnings' not in result:
                result['warnings'] = []
            
        except Exception as analysis_error:
            logger.error(f"Error during symptom analysis: {str(analysis_error)}")
            return jsonify({
                'success': False,
                'error': 'An error occurred during symptom analysis. Please try again.'
            }), 500
        
        # Translate results to target language if needed
        if target_language != 'en':
            try:
                result = translate_analysis_results(result, target_language)
            except Exception as translation_error:
                logger.warning(f"Translation failed: {str(translation_error)}")
                # Continue with English results if translation fails
        
        return jsonify({
            'success': True,
            'data': result,
            'detected_language': detected_language,
            'target_language': target_language
        })
        
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while analyzing symptoms. Please try again.'
        }), 500

@main_bp.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Medical Symptoms-to-Diagnosis Agent is running'
    })

@main_bp.route('/disclaimer')
def disclaimer():
    """Medical disclaimer page"""
    return render_template('disclaimer.html')

@main_bp.route('/disease-info/<disease_name>')
def disease_info(disease_name):
    """Get detailed information about a specific disease"""
    try:
        # For now, return basic information
        # In a full implementation, this would fetch from a medical database
        return jsonify({
            'success': True,
            'disease_name': disease_name,
            'description': f'Detailed information about {disease_name}',
            'symptoms': [],
            'causes': [],
            'treatments': [],
            'prevention': []
        })
    except Exception as e:
        logger.error(f"Error getting disease info: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve disease information'
        }), 500

@main_bp.route('/supported-languages')
def supported_languages():
    """Get list of supported languages"""
    return jsonify({
        'success': True,
        'languages': [
            {'code': 'en', 'name': 'English'},
            {'code': 'hi', 'name': 'Hindi'},
            {'code': 'ur', 'name': 'Urdu'}
        ]
    }) 