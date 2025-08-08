from flask import Flask
from config import Config
import os

def create_app(config_class=Config):
    """Application factory pattern for Flask app"""
    # Create Flask app with correct template folder path
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    app.config.from_object(config_class)
    
    # Initialize extensions here if needed
    
    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app 