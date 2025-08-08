#!/usr/bin/env python3
"""
Medical Symptoms-to-Diagnosis Agent
Main application entry point
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    print("🚀 Starting Medical Symptoms-to-Diagnosis Agent...")
    print("📋 This application is for educational purposes only.")
    print("⚠️  Always consult healthcare professionals for medical advice.")
    print("🌐 Access the application at: http://localhost:5000")
    print("=" * 60)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    ) 