from flask import Flask
from flask_cors import CORS
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    from .agents.ecom_agent.routes import ecom_bp
    app.register_blueprint(ecom_bp, url_prefix='/api/ecom')
    
    return app 