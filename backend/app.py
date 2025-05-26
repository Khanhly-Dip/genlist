from flask import Flask, send_from_directory, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
import sys
from app.agents.ecom_agent import ecom_bp
import json


# app.register_blueprint(ecom_bp, url_prefix='/api/ecom')

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)  # Use stdout instead of stderr
    ]
)

# Set the encoding for stdout and stderr
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configure app
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    
    # Get the absolute path to the frontend directory
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
    app.config['FRONTEND_DIR'] = frontend_dir
    
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
    
    @app.route('/')
    def index():
        return {
            'message': 'Welcome to the E-commerce Content Generation API',
            'endpoints': {
                '/api/ecom/generate': 'POST - Generate content for a single product',
                '/api/ecom/test-batch': 'POST - Generate content for multiple products',
                '/api/ecom/batch': 'POST - Generate content for multiple products in batch',
                '/health': 'GET - Health check endpoint'
            }
        }, 200

    @app.route('/api/ecom/generate')
    def serve_frontend():
        logger.info(f"Serving frontend from: {app.config['FRONTEND_DIR']}")
        return send_from_directory(app.config['FRONTEND_DIR'], 'index.html')
    
    @app.route('/api/ecom/batch', methods=['POST'])
    def batch_generate():
        try:
            # Get the raw data and decode it properly
            raw_data = request.get_data()
            try:
                data = json.loads(raw_data.decode('utf-8'))
            except UnicodeDecodeError:
                # Try with different encoding if UTF-8 fails
                data = json.loads(raw_data.decode('latin-1'))
            
            # Validate that data is a list
            if not isinstance(data, list):
                return {'error': 'Request body must be a list of products'}, 400
                
            if len(data) > 50:
                return {'error': 'Maximum batch size is 50 products'}, 400
                
            # Validate each product in the list
            for product in data:
                if not isinstance(product, dict):
                    return {'error': 'Each product must be a dictionary'}, 400
                if 'title' not in product or 'product_description' not in product:
                    return {'error': 'Each product must have title and product_description fields'}, 400
            
            # Import and use the batch generator
            from app.agents.ecom_agent.services.batch_logic import batch_generator
            results = batch_generator.process_batch(data)
            
            return {
                'status': 'success',
                'total_products': len(data),
                'processed_products': len(results),
                'results': results
            }, 200
            
        except Exception as e:
            logger.error(f"Error processing batch request: {str(e)}")
            return {'error': str(e)}, 500

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5001))
    logger.info(f"Starting Flask application on port {port}")
    app.run(debug=os.getenv('FLASK_DEBUG', 'True') == 'True',
            host=os.getenv('FLASK_HOST', '0.0.0.0'),
            port=port) 