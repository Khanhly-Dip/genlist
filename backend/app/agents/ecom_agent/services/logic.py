from flask import Blueprint, request, jsonify
from ..schemas.request import ProductInput, BatchProductRequest
from ..schemas.response import GeneratedContent, BatchContentGenerationResponse
import logging
import json
import os
from openai import OpenAI
import time
import httpx
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

logger = logging.getLogger(__name__)
ecom_bp = Blueprint('ecom', __name__)

class AmazonListingGenerator:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        logger.info("Checking OPENAI_API_KEY: %s", "Found" if api_key else "Not found")
        if not api_key:
            raise ValueError("Không tìm thấy OPENAI_API_KEY trong file .env")
        
        # Tạo custom HTTP client không sử dụng proxy
        http_client = httpx.Client(
            timeout=30.0,
            verify=True
        )
        
        # Khởi tạo OpenAI client với custom HTTP client
        self.client = OpenAI(
            api_key=api_key,
            http_client=http_client
        )

    def generate_listing(self, input_data: dict) -> dict:
        try:
            logger.info("Starting generate_listing with input: %s", input_data)
            if not input_data["title"]:
                raise ValueError("Tiêu đề sản phẩm là bắt buộc")
            
            # Tạo prompt cho OpenAI
            prompt = f"""
            Bạn là chuyên gia viết nội dung SEO cho sản phẩm của Amazon Seller Central. Hãy tạo content hấp dẫn, sáng tạo và chuẩn SEO, câu từ uyển chuyển, ngôn từ tự nhiên, không lặp từ, tăng tỷ lệ chuyển đổi từ thông tin sản phẩm dưới đây.

## THÔNG TIN SẢN PHẨM:
- Tiêu đề gốc: {input_data['title']}
- Loại sản phẩm (Product Type): {input_data['product_type']}
- Màu sắc: {input_data['color']}
- Kích thước (Size): {input_data['size']}
- Trọng lượng phù hợp: {input_data['weight']}
- Chất liệu: {input_data['material_type']}
- Từ khóa chung (phân tách bằng dấu phẩy): {', '.join(input_data['generic_keywords'])}
- Mô tả sản phẩm ban đầu: {input_data['product_description']}

## YÊU CẦU:
1. **Tiêu đề sản phẩm (SEO Title)**: Viết tiêu đề dài 100–200 ký tự, chèn từ khóa chính tự nhiên, hấp dẫn người mua, tạo được thu hút ngay khi đọc, có thể trích xuất thêm từ mô tả sản phẩm ban đầu vào tiêu đề và thân thiện với công cụ tìm kiếm.
2. **Bullet points (Tính năng nổi bật)**: Viết 5 gạch đầu dòng giới thiệu nhấn mạnh lợi ích, các đặc điểm vượt trội của sản phẩm. Giọng văn thân thiện, tự nhiên, thuyết phục khách hàng lựa chọn.
3. **Mô tả chi tiết (HTML Description)**:
    - Viết một đoạn mô tả dài 300–500 từ.
    - Chia bố cục rõ ràng bằng các thẻ HTML như <h2>, <p>, <ul>, <li>, <strong>.
    - Mở đầu hấp dẫn, giới thiệu sản phẩm theo hướng giải quyết vấn đề cho khách hàng.
    - Phần giữa trình bày thông tin kỹ thuật, chất liệu, kích thước, công dụng.
    - Phần cuối khuyến khích mua hàng, kêu gọi hành động (CTA).
    - Dùng từ đồng nghĩa hợp lý để tránh trùng lặp từ khóa, nhưng vẫn giữ chuẩn SEO và thân thiện với voice search.
4. Truyền generic_keywords dưới dạng chuỗi, cách nhau bằng dấu ;

## ĐỊNH DẠNG ĐẦU RA:
Trả về đúng định dạng JSON bên dưới:

{{
    "title": "Tiêu đề sản phẩm tối ưu SEO",
    "feed_product": {{
        "item_type": "{input_data['product_type']}",
        "standard_price": "Liên hệ",
        "color": "{input_data['color']}",
        "size": "{input_data['size']}",
        "material_type": "{input_data['material_type']}",
        "generic_keywords": "{', '.join(input_data['generic_keywords'])}"
    }},
    "short_description": "<ul><li>Bullet point 1</li><li>Bullet point 2</li><li>...</li></ul>",
    "description": "<h2>Giới thiệu sản phẩm</h2><p>...</p><h2>Thông tin chi tiết</h2><ul><li>...</li></ul><p>...</p>"
}}
            """
            
            start_time = time.time()
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Bạn là một chuyên gia tạo nội dung cho Amazon Seller Central. Hãy trả về kết quả dưới dạng JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            logger.info("OpenAI API call took %s seconds", time.time() - start_time)
            
            # Lấy nội dung từ response
            content = response.choices[0].message.content.strip()
            logger.info("OpenAI response content: %s", content)
            
            try:
                # Clean the response content
                content = content.strip()
                # Remove markdown code block if present
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                content = content.strip()

                # Try to find JSON content
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    content = content[start_idx:end_idx]

                result = json.loads(content)
                logger.info("Parsed JSON result: %s", json.dumps(result, indent=2))

                # Validate required fields
                required_fields = ["title", "feed_product", "short_description", "description"]
                for field in required_fields:
                    if field not in result:
                        raise ValueError(f"Thiếu trường bắt buộc: {field}")
                
                # Validate feed_product fields
                feed_product_fields = ["item_type", "standard_price", "color", "size", "material_type", "generic_keywords"]
                for field in feed_product_fields:
                    if field not in result["feed_product"]:
                        raise ValueError(f"Thiếu trường bắt buộc trong feed_product: {field}")
                
                return result
            except json.JSONDecodeError as e:
                logger.error("JSON parsing error: %s", str(e))
                logger.error("Content that failed to parse: %s", content)
                raise ValueError(f"Lỗi khi parse kết quả JSON: {str(e)}")
                
        except Exception as e:
            logger.error("Error in generate_listing: %s", str(e))
            return {
                "error": str(e)
            }

    def generate_batch_listings(self, products: List[dict]) -> List[dict]:
        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_product = {executor.submit(self.generate_listing, product): product for product in products}
            for future in as_completed(future_to_product):
                product = future_to_product[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error processing product {product['title']}: {str(e)}")
                    results.append({"error": str(e), "product": product})
        return results

generator = AmazonListingGenerator() 