import unittest
from ..services.batch_logic import BatchListingGenerator
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestBatchLogic(unittest.TestCase):
    def setUp(self):
        self.batch_generator = BatchListingGenerator()
        
        # Sample test data
        self.test_products = [
            {
                "title": "Áo thun nam cotton 100% màu đen size M",
                "product_description": "Áo thun nam cotton 100% màu đen size M, chất liệu thoáng mát, thấm hút mồ hôi tốt, phù hợp cho mùa hè"
            },
            {
                "title": "Quần jean nam slim fit màu xanh",
                "product_description": "Quần jean nam slim fit màu xanh, chất liệu cotton denim cao cấp, co giãn 4 chiều, kiểu dáng hiện đại"
            }
        ]

    def test_batch_processing(self):
        """Test basic batch processing functionality"""
        results = self.batch_generator.process_batch(self.test_products)
        
        # Check if we got results for all products
        self.assertEqual(len(results), len(self.test_products))
        
        # Check structure of each result
        for result in results:
            self.assertIn('title', result)
            self.assertIn('bullet_points', result)
            self.assertIn('description', result)
            self.assertIn('original_product', result)
            
            # Check if bullet points are in correct HTML format
            self.assertTrue(result['bullet_points'].startswith('<ul>'))
            self.assertTrue(result['bullet_points'].endswith('</ul>'))
            
            # Check if description has required sections
            self.assertIn('<h2>Giới thiệu sản phẩm</h2>', result['description'])
            self.assertIn('<h2>Tính năng nổi bật</h2>', result['description'])
            self.assertIn('<h2>Thông tin chi tiết</h2>', result['description'])

    def test_error_handling(self):
        """Test error handling with invalid input"""
        invalid_products = [
            {
                "title": "",  # Empty title should cause error
                "product_description": "Test description"
            },
            {
                "title": "Valid product",
                "product_description": "Valid description"
            }
        ]
        
        results = self.batch_generator.process_batch(invalid_products)
        
        # Check if we got results for all products
        self.assertEqual(len(results), len(invalid_products))
        
        # First result should have error
        self.assertIn('error', results[0])
        
        # Second result should be valid
        self.assertIn('title', results[1])
        self.assertIn('bullet_points', results[1])
        self.assertIn('description', results[1])

    def test_concurrent_processing(self):
        """Test concurrent processing with multiple products"""
        # Create 50 test products
        large_batch = []
        for i in range(50):
            large_batch.append({
                "title": f"Test Product {i}",
                "product_description": f"Test Description {i}"
            })
        
        results = self.batch_generator.process_batch(large_batch)
        
        # Check if all products were processed
        self.assertEqual(len(results), len(large_batch))
        
        # Check if results are unique
        titles = [r['title'] for r in results if 'title' in r]
        self.assertEqual(len(set(titles)), len(titles))

    def test_response_format(self):
        """Test the format of generated content"""
        results = self.batch_generator.process_batch(self.test_products)
        
        for result in results:
            if 'error' not in result:
                # Check title length
                self.assertLessEqual(len(result['title']), 150)
                
                # Check bullet points format
                bullet_points = result['bullet_points']
                self.assertTrue(bullet_points.startswith('<ul>'))
                self.assertTrue(bullet_points.endswith('</ul>'))
                self.assertEqual(bullet_points.count('<li>'), 5)  # Should have 5 bullet points
                
                # Check description format
                description = result['description']
                self.assertIn('<h2>Giới thiệu sản phẩm</h2>', description)
                self.assertIn('<h2>Tính năng nổi bật</h2>', description)
                self.assertIn('<h2>Thông tin chi tiết</h2>', description)

if __name__ == '__main__':
    unittest.main() 