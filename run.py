#!/usr/bin/env python3
"""
Medical Symptoms-to-Diagnosis Agent
Main application entry point
"""

import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    print("🚀 Starting Medical Symptoms-to-Diagnosis Agent...")
    print("📋 This application is for educational purposes only.")
    print("⚠️  Always consult healthcare professionals for medical advice.")
    
    # Get port from environment variable (Vercel sets this)
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🌐 Access the application at: http://localhost:{port}")
    print("=" * 60)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Set to False for production deployment
    ) 