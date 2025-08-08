from flask import Blueprint, request, jsonify, render_template
from app.utils import analyze_symptoms, validate_symptoms_input, detect_language, translate_analysis_results
from app.chatbot_doctor import chatbot
from app.image_recognition import medical_image_analyzer
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

@main_bp.route('/chat_with_doctor', methods=['POST'])
def chat_with_doctor():
    """Chat with AI doctor"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            })
        
        # Get response from chatbot
        result = chatbot.chat_with_doctor(message, session_id)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in chat_with_doctor: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'response': 'I apologize, but I\'m experiencing technical difficulties. Please try again later.'
        })

@main_bp.route('/chat_session_info/<session_id>')
def chat_session_info(session_id):
    """Get information about a chat session"""
    try:
        session_info = chatbot.get_session_info(session_id)
        if session_info:
            return jsonify({
                'success': True,
                'session_info': session_info
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error getting session info: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve session information'
        }), 500

@main_bp.route('/analyze_image', methods=['POST'])
def analyze_image():
    """Analyze medical image and provide diagnosis/recommendations"""
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided'
            }), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No image file selected'
            }), 400
        
        # Get additional data
        user_description = request.form.get('description', '')
        session_id = request.form.get('session_id', '')
        
        # Read image data
        image_data = image_file.read()
        
        # Validate file size
        max_size = medical_image_analyzer.get_max_file_size()
        if len(image_data) > max_size:
            return jsonify({
                'success': False,
                'error': f'Image file is too large. Maximum size is {max_size // (1024*1024)}MB'
            }), 400
        
        # Analyze image
        if session_id:
            # Use chatbot integration for chat sessions
            result = chatbot.analyze_image_in_chat(image_data, user_description, session_id)
            return jsonify(result)
        else:
            # Direct image analysis
            result = medical_image_analyzer.analyze_medical_image(image_data, user_description)
            return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to analyze image: {str(e)}'
        }), 500

@main_bp.route('/image_supported_formats')
def image_supported_formats():
    """Get supported image formats"""
    return jsonify({
        'success': True,
        'supported_formats': medical_image_analyzer.get_supported_formats(),
        'max_file_size_mb': medical_image_analyzer.get_max_file_size() // (1024 * 1024)
    }) 