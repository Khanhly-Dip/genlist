from flask import Blueprint, request, jsonify, send_from_directory, current_app
from ..services.logic import generator
from ..schemas.request import ProductInput, BatchProductRequest
from ..schemas.response import GeneratedContent, BatchContentGenerationResponse
import logging
import os

logger = logging.getLogger(__name__)
ecom_bp = Blueprint('ecom', __name__)

@ecom_bp.route('/generate', methods=['GET', 'POST'])
def generate_content():
    if request.method == 'GET':
        logger.info(f"Serving frontend from blueprint: {current_app.config['FRONTEND_DIR']}")
        return send_from_directory(current_app.config['FRONTEND_DIR'], 'index.html')
        
    try:
        data = request.get_json()
        # Validate input data
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Generate content using the generator
        result = generator.generate_listing(data)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        return jsonify({"error": str(e)}), 400

@ecom_bp.route('/test-batch', methods=['POST'])
def test_batch():
    try:
        data = request.get_json()
        batch_request = BatchProductRequest(**data)
        results = generator.generate_batch_listings([p.dict() for p in batch_request.products])
        return jsonify({"results": results}), 200
    except Exception as e:
        logger.error(f"Error in test_batch: {str(e)}")
        return jsonify({"error": str(e)}), 400 