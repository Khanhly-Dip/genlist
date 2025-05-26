from flask import Blueprint, request, jsonify
from typing import List
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from .logic import AmazonListingGenerator

logger = logging.getLogger(__name__)
batch_bp = Blueprint('batch', __name__)

class BatchListingGenerator:
    def __init__(self):
        self.generator = AmazonListingGenerator()

    def process_batch(self, products: List[dict]) -> List[dict]:
        """
        Process a batch of products concurrently
        Args:
            products: List of product dictionaries, each containing title and product_description
        Returns:
            List of processed products with their generated content
        """
        results = []
        with ThreadPoolExecutor(max_workers=50) as executor:
            # Submit all tasks
            future_to_product = {
                executor.submit(self.generator.generate_listing, product): product 
                for product in products
            }
            
            # Process completed tasks as they finish
            for future in as_completed(future_to_product):
                product = future_to_product[future]
                try:
                    result = future.result()
                    # Add original product info to result
                    result['original_product'] = {
                        'title': product.get('title'),
                        'product_description': product.get('product_description')
                    }
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error processing product {product.get('title', 'Unknown')}: {str(e)}")
                    results.append({
                        "error": str(e),
                        "original_product": product
                    })
        return results

batch_generator = BatchListingGenerator()

@batch_bp.route('/process-batch', methods=['POST'])
def process_batch():
    """
    Process a batch of products (up to 50) concurrently
    Request body should be a list of products, each containing:
    {
        "title": "Product title",
        "product_description": "Product description"
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not isinstance(data, list):
            return jsonify({
                "error": "Request body must be a list of products"
            }), 400
            
        if len(data) > 50:
            return jsonify({
                "error": "Maximum batch size is 50 products"
            }), 400
            
        # Validate each product in the list
        for product in data:
            if not isinstance(product, dict):
                return jsonify({
                    "error": "Each product must be a dictionary"
                }), 400
            if 'title' not in product or 'product_description' not in product:
                return jsonify({
                    "error": "Each product must have 'title' and 'product_description' fields"
                }), 400
        
        # Process the batch
        results = batch_generator.process_batch(data)
        
        return jsonify({
            "status": "success",
            "total_products": len(data),
            "processed_products": len(results),
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}")
        return jsonify({
            "error": str(e)
        }), 500 