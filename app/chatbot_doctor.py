#!/usr/bin/env python3
"""
Medical Chatbot Doctor Module
Provides conversational AI interface for medical consultations
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
import json
from app.ai_providers import ai_providers
from app.image_recognition import medical_image_analyzer
from langdetect import detect, LangDetectException

logger = logging.getLogger(__name__)

class MedicalChatbot:
    """Medical chatbot that acts as a virtual doctor"""
    
    def __init__(self):
        """Initialize the medical chatbot"""
        self.ai_provider = ai_providers
        self.sessions = {}
        logger.info("🤖 Medical Chatbot initialized")
    
    def detect_language(self, text: str) -> str:
        """Detect the language of the input text"""
        try:
            lang = detect(text)
            return lang
        except LangDetectException:
            return 'en'  # Default to English if detection fails
    
    def _create_multilingual_prompt(self, user_message: str, conversation_history: List, patient_context: Dict, detected_language: str) -> str:
        """Create a multilingual prompt for the AI"""
        
        # Enhanced language mapping for Indian languages
        language_mapping = {
            'hi': 'Hindi',
            'bn': 'Bengali', 
            'te': 'Telugu',
            'ta': 'Tamil',
            'mr': 'Marathi',
            'gu': 'Gujarati',
            'kn': 'Kannada',
            'ml': 'Malayalam',
            'pa': 'Punjabi',
            'ur': 'Urdu',
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ar': 'Arabic',
            'pt': 'Portuguese',
            'ru': 'Russian'
        }
        
        # Language-specific greetings and instructions
        language_greetings = {
            'en': "Hello! I'm Dr. AI, your medical assistant. How can I help you today?",
            'es': "¡Hola! Soy el Dr. IA, su asistente médico. ¿Cómo puedo ayudarle hoy?",
            'fr': "Bonjour! Je suis Dr. IA, votre assistant médical. Comment puis-je vous aider aujourd'hui?",
            'de': "Hallo! Ich bin Dr. KI, Ihr medizinischer Assistent. Wie kann ich Ihnen heute helfen?",
            'hi': "नमस्ते! मैं डॉ. एआई हूं, आपका चिकित्सीय सहायक। मैं आज आपकी कैसे मदद कर सकता हूं?",
            'bn': "হ্যালো! আমি ডাঃ এআই, আপনার চিকিৎসা সহকারী। আজ আমি কীভাবে আপনাকে সাহায্য করতে পারি?",
            'te': "నమస్కారం! నేను డాక్టర్ ఎఐ, మీ వైద్య సహాయకుడు. నేను ఈరోజు మీకు ఎలా సహాయపడగలను?",
            'ta': "வணக்கம்! நான் டாக்டர் ஏஐ, உங்கள் மருத்துவ உதவியாளர். நான் இன்று உங்களுக்கு எப்படி உதவ முடியும்?",
            'mr': "नमस्कार! मी डॉ. एआय, तुमचा वैद्यकीय सहाय्यक. मी आज तुमची कशी मदत करू शकतो?",
            'gu': "નમસ્તે! હું ડૉ. એઆઈ, તમારો વૈદ્યકીય સહાયક. હું આજે તમારી કેવી રીતે મદદ કરી શકું?",
            'kn': "ನಮಸ್ಕಾರ! ನಾನು ಡಾ. ಎಐ, ನಿಮ್ಮ ವೈದ್ಯಕೀಯ ಸಹಾಯಕ. ನಾನು ಇಂದು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
            'ml': "നമസ്കാരം! ഞാൻ ഡോ. എഐ, നിങ്ങളുടെ വൈദ്യ സഹായി. ഞാൻ ഇന്ന് നിങ്ങളെ എങ്ങനെ സഹായിക്കാം?",
            'pa': "ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਡਾ. ਏਆਈ, ਤੁਹਾਡਾ ਵੈਦਕੀ ਸਹਾਇਕ. ਮੈਂ ਅੱਜ ਤੁਹਾਡੀ ਕਿਵੇਂ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ?",
            'ur': "السلام علیکم! میں ڈاکٹر اے آئی، آپ کا طبی معاون۔ میں آج آپ کی کیسے مدد کر سکتا ہوں؟",
            'zh': "您好！我是AI医生，您的医疗助手。今天我能为您做些什么？",
            'ja': "こんにちは！私はAI医師、あなたの医療アシスタントです。今日はどのようにお手伝いできますか？",
            'ar': "مرحباً! أنا الدكتور الذكي، مساعدك الطبي. كيف يمكنني مساعدتك اليوم؟",
            'pt': "Olá! Sou o Dr. IA, seu assistente médico. Como posso ajudá-lo hoje?",
            'ru': "Здравствуйте! Я доктор ИИ, ваш медицинский помощник. Как я могу вам помочь сегодня?"
        }
        
        # Get appropriate greeting for detected language
        greeting = language_greetings.get(detected_language, language_greetings['en'])
        
        # Enhanced language-specific instructions with stronger emphasis on same language response
        language_instructions = {
            'en': "CRITICAL: You MUST respond in English only. Be professional, empathetic, and provide helpful medical guidance while always recommending consultation with healthcare professionals for serious concerns.",
            'es': "CRÍTICO: DEBES responder SOLO en español. Sé profesional, empático y proporciona orientación médica útil, siempre recomendando consultar con profesionales de la salud para problemas graves.",
            'fr': "CRITIQUE: Vous DEVEZ répondre UNIQUEMENT en français. Soyez professionnel, empathique et fournissez des conseils médicaux utiles tout en recommandant toujours de consulter des professionnels de la santé pour les préoccupations graves.",
            'de': "KRITISCH: Sie MÜSSEN NUR auf Deutsch antworten. Seien Sie professionell, einfühlsam und geben Sie hilfreiche medizinische Beratung, während Sie immer eine Konsultation mit medizinischen Fachkräften für ernste Anliegen empfehlen.",
            'hi': "महत्वपूर्ण: आपको हिंग्लिश (Hindi + English mixed) में जवाब देना चाहिए। इंडोनेशियन (ID) में कभी नहीं। पूरी तरह से अंग्रेजी में कभी नहीं। हिंग्लिश में जवाब दें - हिंदी के साथ अंग्रेजी शब्दों का मिश्रण करें। जैसे: 'आपको headache है', 'doctor से consult करें', 'medicine लें', 'symptoms बताएं', 'treatment के लिए', 'medical advice', 'pain relief', 'proper diagnosis'। अंग्रेजी medical terms का ज्यादा use करें। पेशेवर, सहानुभूतिपूर्ण रहें और सहायक चिकित्सीय मार्गदर्शन प्रदान करें, हमेशा गंभीर चिंताओं के लिए स्वास्थ्य पेशेवरों से परामर्श की सिफारिश करें।",
            'bn': "গুরুত্বপূর্ণ: আপনাকে শুধুমাত্র বাংলায় উত্তর দিতে হবে। পেশাদার, সহানুভূতিশীল হন এবং সহায়ক চিকিৎসা গাইডেন্স প্রদান করুন, গুরুতর উদ্বেগের জন্য সর্বদা স্বাস্থ্যসেবা পেশাদারদের সাথে পরামর্শের সুপারিশ করুন।",
            'te': "ముఖ్యమైనది: మీరు తెలుగులో మాత్రమే సమాధానం ఇవ్వాలి. వృత్తిపరమైన, సానుభూతిపరుడై ఉండండి మరియు సహాయక వైద్య మార్గదర్శకత్వాన్ని అందించండి, తీవ్రమైన ఆందోళనల కోసం ఎల్లప్పుడూ ఆరోగ్య సంరక్షణ నిపుణులను సంప్రదించాలని సిఫార్సు చేయండి.",
            'ta': "முக்கியமானது: நீங்கள் தமிழில் மட்டுமே பதிலளிக்க வேண்டும். தொழில்முறை, பச்சாதாபமாக இருங்கள் மற்றும் உதவிகரமான மருத்துவ வழிகாட்டுதலை வழங்குங்கள், கடுமையான கவலைகளுக்கு எப்போதும் சுகாதார நிபுணர்களை ஆலோசிக்க பரிந்துரைக்கவும்.",
            'mr': "महत्वाचे: तुम्ही फक्त मराठीत उत्तर द्यावे. व्यावसायिक, सहानुभूतीशील रहा आणि सहाय्यक वैद्यकीय मार्गदर्शन द्या, गंभीर चिंतांसाठी नेहमी आरोग्य सेवा व्यावसायिकांना सल्ला घेण्याची शिफारस करा.",
            'gu': "મહત્વપૂર્ણ: તમારે ફક્ત ગુજરાતીમાં જવાબ આપવો જોઈએ. વ્યવસાયિક, સહાનુભૂતિશીલ રહો અને સહાયક વૈદ્યકીય માર્ગદર્શન આપો, ગંભીર ચિંતાઓ માટે હંમેશા આરોગ્ય સેવા વ્યવસાયિકોની સલાહ લેવાની ભલામણ કરો.",
            'kn': "ಮುಖ್ಯ: ನೀವು ಕನ್ನಡದಲ್ಲಿ ಮಾತ್ರ ಉತ್ತರಿಸಬೇಕು. ವೃತ್ತಿಪರ, ಸಹಾನುಭೂತಿಯುತವಾಗಿರಿ ಮತ್ತು ಸಹಾಯಕ ವೈದ್ಯಕೀಯ ಮಾರ್ಗದರ್ಶನವನ್ನು ನೀಡಿ, ಗಂಭೀರ ಕಾಳಜಿಗಳಿಗಾಗಿ ಯಾವಾಗಲೂ ಆರೋಗ್ಯ ಸೇವಾ ವೃತ್ತಿಪರರನ್ನು ಸಂಪ್ರದಿಸಲು ಶಿಫಾರಸು ಮಾಡಿ.",
            'ml': "പ്രധാനം: നിങ്ങൾ മലയാളത്തിൽ മാത്രമേ ഉത്തരിക്കേണ്ടതുള്ളൂ. വൃത്തിപരവും സഹാനുഭൂതിയുള്ളതുമായി ആരോഗ്യ സേവാ വൃത്ത ിപരരെ സമീപിക്കാൻ എപ്പോഴും ശുപാർശ ചെയ്യുക.",
            'pa': "ਮਹੱਤਵਪੂਰਨ: ਤੁਹਾਨੂੰ ਸਿਰਫ ਪੰਜਾਬੀ ਵਿੱਚ ਜਵਾਬ ਦੇਣਾ ਚਾਹੀਦਾ ਹੈ। ਪੇਸ਼ੇਵਰ, ਸਹਾਨੁਭੂਤੀਸ਼ੀਲ ਰਹੋ ਅਤੇ ਸਹਾਇਕ ਵੈਦਕੀ ਮਾਰਗਦਰਸ਼ਨ ਦਿਓ, ਗੰਭੀਰ ਚਿੰਤਾਵਾਂ ਲਈ ਹਮੇਸ਼ਾ ਸਿਹਤ ਸੇਵਾ ਪੇਸ਼ੇਵਰਾਂ ਨੂੰ ਸਲਾਹ ਲੈਣ ਦੀ ਸਿਫਾਰਸ਼ ਕਰੋ।",
            'ur': "اہم: آپ کو صرف اردو میں جواب دینا چاہیے۔ پیشہ ورانہ، ہمدردانہ رہیں اور مددگار طبی رہنمائی فراہم کریں، سنگین خدشات کے لیے ہمیشہ صحت کی دیکھ بھال کے پیشہ ور افراد سے مشورہ لینے کی سفارش کریں۔",
            'zh': "重要：您必须只用中文回复。要专业、富有同情心，并提供有用的医疗指导，同时始终建议对严重问题咨询医疗专业人员。",
            'ja': "重要：患者が使用している言語と同じ言語で回答してください。専門的で、共感的であり、有用な医療ガイダンスを提供し、深刻な懸念については常に医療専門家への相談を推奨してください。",
            'ar': "مهم: يجب عليك الرد باللغة العربية فقط. كن مهنياً ومتعاطفاً وقدم إرشادات طبية مفيدة مع التوصية دائماً باستشارة متخصصي الرعاية الصحية للمخاوف الجادة.",
            'pt': "CRÍTICO: Você DEVE responder APENAS em português. Seja profissional, empático e forneça orientação médica útil, sempre recomendando consulta com profissionais de saúde para preocupações graves.",
            'ru': "КРИТИЧНО: Вы ДОЛЖНЫ отвечать ТОЛЬКО на русском языке. Будьте профессиональны, сопереживайте и предоставляйте полезные медицинские советы, всегда рекомендуя консультацию с медицинскими работниками для серьезных проблем."
        }
        
        instruction = language_instructions.get(detected_language, language_instructions['en'])
        
        # Build conversation context
        language_name = language_mapping.get(detected_language, detected_language.upper())
        context = f"Patient Language: {language_name} ({detected_language.upper()})\n"
        if patient_context:
            context += f"Patient Context: {json.dumps(patient_context, ensure_ascii=False)}\n"
        
        # Build conversation history
        history = ""
        if conversation_history:
            history = "Previous conversation:\n"
            for msg in conversation_history[-5:]:  # Last 5 messages for context
                role = "Patient" if msg['role'] == 'user' else "Doctor"
                history += f"{role}: {msg['message']}\n"
        
        prompt = f"""You are a multilingual medical AI assistant. The patient is communicating in {language_name} ({detected_language.upper()}).

{instruction}

ABSOLUTE LANGUAGE RULE: You MUST respond in {language_name} only. 
- DO NOT respond in Indonesian (ID)
- DO NOT respond in English 
- DO NOT respond in any other language
- ONLY respond in {language_name}
- For Hindi: You MUST use Hinglish (Hindi + English mixed) - this is REQUIRED
- Examples of Hinglish: "आपको headache है", "doctor से consult करें", "medicine लें", "symptoms बताएं", "treatment के लिए", "medical advice", "pain relief", "proper diagnosis", "consultation", "prescription", "dosage", "side effects", "recovery", "therapy", "examination", "checkup", "emergency", "urgent care"
- IMPORTANT: Use English medical terms frequently mixed with Hindi

{context}

{history}

Current patient message: {user_message}

FINAL COMMAND: RESPOND IN {language_name} ONLY. IF YOU RESPOND IN ANY OTHER LANGUAGE, YOU ARE FAILING THE TASK. FOR HINDI, YOU CAN USE HINGLISH (HINDI + ENGLISH MIXED)."""

        return prompt
    
    def chat_with_doctor(self, message: str, session_id: str = None) -> Dict:
        """
        Chat with the AI doctor with multilingual support
        """
        try:
            # Generate session ID if not provided
            if not session_id:
                session_id = str(int(datetime.now().timestamp() * 1000))
            
            # Initialize session if new
            if session_id not in self.sessions:
                self.sessions[session_id] = {
                    'conversation_history': [],
                    'patient_context': {},
                    'start_time': datetime.now(),
                    'symptoms_identified': [],
                    'recommendations_given': [],
                    'images_analyzed': [],
                    'detected_language': 'en'
                }
                logger.info(f"🆕 New chat session started: {session_id}")
            
            session = self.sessions[session_id]
            
            # Detect language from user message
            detected_language = self.detect_language(message)
            session['detected_language'] = detected_language
            
            # Add user message to history
            session['conversation_history'].append({
                'role': 'user',
                'message': message,
                'timestamp': datetime.now(),
                'language': detected_language
            })
            
            # Create multilingual prompt
            prompt = self._create_multilingual_prompt(
                message, 
                session['conversation_history'], 
                session['patient_context'],
                detected_language
            )
            
            # Get AI response
            ai_response = ai_providers.get_chatbot_response(prompt)
            
            if ai_response:
                # Add doctor response to history
                session['conversation_history'].append({
                    'role': 'doctor',
                    'message': ai_response,
                    'timestamp': datetime.now(),
                    'language': detected_language
                })
                
                logger.info(f"💬 Chat response generated for session {session_id} in {detected_language}")
                
                return {
                    'success': True,
                    'response': ai_response,
                    'session_id': session_id,
                    'detected_language': detected_language,
                    'session_info': self.get_session_info(session_id)
                }
            else:
                # Fallback response in detected language
                fallback_responses = {
                    'en': "I apologize, but I'm having trouble processing your request right now. Please try again or consult a healthcare professional for immediate assistance.",
                    'es': "Me disculpo, pero estoy teniendo problemas para procesar su solicitud en este momento. Por favor, inténtelo de nuevo o consulte a un profesional de la salud para asistencia inmediata.",
                    'fr': "Je m'excuse, mais j'ai des difficultés à traiter votre demande en ce moment. Veuillez réessayer ou consulter un professionnel de la santé pour une assistance immédiate.",
                    'de': "Es tut mir leid, aber ich habe derzeit Probleme, Ihre Anfrage zu verarbeiten. Bitte versuchen Sie es erneut oder konsultieren Sie einen medizinischen Fachmann für sofortige Hilfe.",
                    'hi': "मैं क्षमा चाहता हूं, लेकिन मुझे आपके अनुरोध को संसाधित करने में समस्या हो रही है। कृपया पुनः प्रयास करें या तत्काल सहायता के लिए स्वास्थ्य पेशेवर से परामर्श करें।",
                    'zh': "很抱歉，我现在处理您的请求时遇到了问题。请重试或咨询医疗专业人员以获得即时帮助。",
                    'ja': "申し訳ございませんが、現在リクエストの処理に問題があります。もう一度お試しいただくか、即座の支援のために医療専門家にご相談ください。",
                    'ar': "أعتذر، لكنني أواجه مشكلة في معالجة طلبك الآن. يرجى المحاولة مرة أخرى أو استشارة متخصص في الرعاية الصحية للحصول على مساعدة فورية.",
                    'pt': "Peço desculpas, mas estou tendo problemas para processar sua solicitação agora. Por favor, tente novamente ou consulte um profissional de saúde para assistência imediata.",
                    'ru': "Приношу извинения, но у меня возникли проблемы с обработкой вашего запроса. Пожалуйста, попробуйте еще раз или обратитесь к медицинскому работнику для немедленной помощи."
                }
                
                fallback = fallback_responses.get(detected_language, fallback_responses['en'])
                
                return {
                    'success': False,
                    'response': fallback,
                    'session_id': session_id,
                    'detected_language': detected_language,
                    'error': 'AI response generation failed'
                }
                
        except Exception as e:
            logger.error(f"❌ Error in chat with doctor: {str(e)}")
            return {
                'success': False,
                'response': "I apologize, but I'm experiencing technical difficulties. Please try again later or consult a healthcare professional.",
                'session_id': session_id,
                'detected_language': 'en',
                'error': str(e)
            }
    
    def analyze_image_in_chat(self, image_data: bytes, user_description: str, session_id: str) -> Dict:
        """
        Analyze medical image within chat context with multilingual support
        """
        try:
            # Initialize session if new
            if session_id not in self.sessions:
                self.sessions[session_id] = {
                    'conversation_history': [],
                    'patient_context': {},
                    'start_time': datetime.now(),
                    'symptoms_identified': [],
                    'recommendations_given': [],
                    'images_analyzed': []
                }
                logger.info(f"🆕 New chat session with image analysis: {session_id}")
            
            session = self.sessions[session_id]
            
            # Detect language from user description
            detected_language = self.detect_language(user_description) if user_description else 'en'
            session['detected_language'] = detected_language
            
            # Analyze the image
            analysis_result = medical_image_analyzer.analyze_medical_image(image_data, user_description)
            
            # Add image analysis to session
            session['images_analyzed'].append({
                'timestamp': datetime.now(),
                'description': user_description,
                'analysis': analysis_result,
                'language': detected_language
            })
            
            # Create chat response from analysis in detected language
            chat_response = self._create_image_analysis_response(analysis_result, user_description, detected_language)
            
            # Add to conversation history
            session['conversation_history'].append({
                'role': 'user',
                'message': f"[Image Upload] {user_description if user_description else 'Medical image uploaded'}",
                'timestamp': datetime.now(),
                'type': 'image_upload',
                'language': detected_language
            })
            
            session['conversation_history'].append({
                'role': 'doctor',
                'message': chat_response,
                'timestamp': datetime.now(),
                'type': 'image_analysis',
                'language': detected_language
            })
            
            logger.info(f"🖼️ Image analysis completed for session {session_id}")
            return {
                'success': True,
                'chat_response': chat_response,
                'analysis_result': analysis_result,
                'detected_language': detected_language
            }
            
        except Exception as e:
            logger.error(f"❌ Error in image analysis chat: {str(e)}")
            return {
                'success': False,
                'error': f"Failed to analyze image: {str(e)}",
                'chat_response': "I apologize, but I'm having trouble analyzing the image. Please try uploading a clearer image or describe your symptoms in text.",
                'detected_language': 'en'
            }
    
    def _create_image_analysis_response(self, analysis_result: Dict, user_description: str, language: str = 'en') -> str:
        """
        Create a conversational response from image analysis in the detected language
        """
        try:
            if not analysis_result or not analysis_result.get('image_analysis'):
                return self._get_fallback_response(language)
            
            analysis = analysis_result['image_analysis']
            user_query_addressed = analysis_result.get('user_query_addressed', '')
            
            # Language-specific response templates
            response_templates = {
                'en': {
                    'intro': f"Based on my analysis of your image{f' and your question about {user_query_addressed}' if user_query_addressed else ''}, here's what I found:",
                    'findings': "Visual findings:",
                    'conditions': "Potential conditions identified:",
                    'recommendations': "Recommendations:",
                    'urgent': "⚠️ URGENT: Please seek immediate medical attention if you experience:",
                    'consult': "Please consult a healthcare professional for proper diagnosis and treatment."
                },
                'es': {
                    'intro': f"Basándome en mi análisis de su imagen{f' y su pregunta sobre {user_query_addressed}' if user_query_addressed else ''}, esto es lo que encontré:",
                    'findings': "Hallazgos visuales:",
                    'conditions': "Condiciones potenciales identificadas:",
                    'recommendations': "Recomendaciones:",
                    'urgent': "⚠️ URGENTE: Busque atención médica inmediata si experimenta:",
                    'consult': "Por favor, consulte a un profesional de la salud para un diagnóstico y tratamiento adecuados."
                },
                'fr': {
                    'intro': f"Basé sur mon analyse de votre image{f' et votre question sur {user_query_addressed}' if user_query_addressed else ''}, voici ce que j'ai trouvé:",
                    'findings': "Trouvailles visuelles:",
                    'conditions': "Conditions potentielles identifiées:",
                    'recommendations': "Recommandations:",
                    'urgent': "⚠️ URGENT: Veuillez consulter immédiatement un médecin si vous ressentez:",
                    'consult': "Veuillez consulter un professionnel de la santé pour un diagnostic et un traitement appropriés."
                },
                'hi': {
                    'intro': f"आपकी छवि के विश्लेषण के आधार पर{f' और {user_query_addressed} के बारे में आपके प्रश्न के आधार पर' if user_query_addressed else ''}, यहाँ मैंने क्या पाया:",
                    'findings': "दृश्य निष्कर्ष:",
                    'conditions': "पहचानी गई संभावित स्थितियां:",
                    'recommendations': "सिफारिशें:",
                    'urgent': "⚠️ तत्काल: यदि आप अनुभव करते हैं तो तुरंत चिकित्सा सहायता लें:",
                    'consult': "उचित निदान और उपचार के लिए कृपया स्वास्थ्य पेशेवर से परामर्श करें।"
                },
                'zh': {
                    'intro': f"根据我对您图像的分析{f'以及您关于{user_query_addressed}的问题' if user_query_addressed else ''}，以下是我的发现:",
                    'findings': "视觉发现:",
                    'conditions': "识别的潜在状况:",
                    'recommendations': "建议:",
                    'urgent': "⚠️ 紧急: 如果您出现以下症状，请立即就医:",
                    'consult': "请咨询医疗专业人员以获得正确的诊断和治疗。"
                }
            }
            
            template = response_templates.get(language, response_templates['en'])
            
            response = f"{template['intro']}\n\n"
            
            # Add visual findings
            if analysis.get('visual_findings'):
                response += f"{template['findings']}\n"
                for finding in analysis['visual_findings']:
                    response += f"• {finding}\n"
                response += "\n"
            
            # Add potential conditions
            if analysis.get('potential_conditions'):
                response += f"{template['conditions']}\n"
                for condition in analysis['potential_conditions']:
                    confidence = condition.get('confidence', 0)
                    severity = condition.get('severity', 'unknown')
                    description = condition.get('description', '')
                    response += f"• {condition.get('condition', 'Unknown')} (Confidence: {confidence}%, Severity: {severity})\n"
                    if description:
                        response += f"  {description}\n"
                response += "\n"
            
            # Add recommendations
            if analysis.get('recommendations'):
                response += f"{template['recommendations']}\n"
                for rec in analysis['recommendations']:
                    response += f"• {rec}\n"
                response += "\n"
            
            # Add urgent warnings
            if analysis.get('immediate_actions'):
                response += f"{template['urgent']}\n"
                for action in analysis['immediate_actions']:
                    response += f"• {action}\n"
                response += "\n"
            
            response += template['consult']
            
            return response
            
        except Exception as e:
            logger.error(f"Error creating image analysis response: {str(e)}")
            return self._get_fallback_response(language)
    
    def _get_fallback_response(self, language: str) -> str:
        """Get fallback response in the specified language"""
        fallback_responses = {
            'en': "I've analyzed your image, but I need more information to provide a complete assessment. Please describe your symptoms and concerns in detail.",
            'es': "He analizado su imagen, pero necesito más información para proporcionar una evaluación completa. Por favor, describa sus síntomas y preocupaciones en detalle.",
            'fr': "J'ai analysé votre image, mais j'ai besoin de plus d'informations pour fournir une évaluation complète. Veuillez décrire vos symptômes et préoccupations en détail.",
            'hi': "मैंने आपकी छवि का विश्लेषण किया है, लेकिन पूर्ण मूल्यांकन प्रदान करने के लिए मुझे अधिक जानकारी की आवश्यकता है। कृपया अपने लक्षणों और चिंताओं का विस्तार से वर्णन करें।",
            'zh': "我已经分析了您的图像，但需要更多信息来提供完整的评估。请详细描述您的症状和担忧。"
        }
        return fallback_responses.get(language, fallback_responses['en'])
    
    def get_session_info(self, session_id: str) -> Dict:
        """Get information about a chat session"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            return {
                'session_id': session_id,
                'start_time': session['start_time'].isoformat(),
                'message_count': len(session['conversation_history']),
                'images_analyzed': len(session['images_analyzed']),
                'detected_language': session.get('detected_language', 'en'),
                'symptoms_identified': session['symptoms_identified'],
                'recommendations_given': session['recommendations_given']
            }
        return {}
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a chat session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

# Global instance
chatbot = MedicalChatbot() 