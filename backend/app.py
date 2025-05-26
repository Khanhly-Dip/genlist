from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from app.agents.ecom_agent import ecom_bp


# app.register_blueprint(ecom_bp, url_prefix='/api/ecom')

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configure app
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    
    # Configure CORS
    CORS(app, resources={
        r"/*": {
            "origins": [
                "https://apiecom.teamexp.net",
                "https://ecom.teamexp.net",
                "http://localhost:3000",
            ],
            "supports_credentials": True,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": [
                "Content-Type", 
                "Authorization",
                "X-Requested-With",
                "Accept",
                "Origin",
                "Access-Control-Request-Method",
                "Access-Control-Request-Headers"
            ],
            "expose_headers": ["Content-Type", "Authorization"],
            "max_age": 3600
        }
    })
    
    # Register blueprints
    from app.agents.ecom_agent import ecom_bp
    app.register_blueprint(ecom_bp, url_prefix='/api/ecom')
    
    @app.route('/health')
    def health_check():
        logger.info("Health check endpoint called")
        return {'status': 'healthy'}, 200
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5001))
    logger.info(f"Starting Flask application on port {port}")
    app.run(debug=os.getenv('FLASK_DEBUG', 'True') == 'True',
            host=os.getenv('FLASK_HOST', '0.0.0.0'),
            port=port) 