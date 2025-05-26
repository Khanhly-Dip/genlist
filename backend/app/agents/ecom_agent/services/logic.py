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

    Emotional_Keywords = {
        "Gift_Appeal": ["Great for Gifts", "Birthday Gift", "Christmas Gift", "Mother's Day Gift", "Valentine's Day Gift", "Anniversary Gift", "For Him / For Her"],
        "Comfort_Cozy": ["Cozy", "Warm", "Comfortable", "Relaxing", "Soft Touch", "Soothing", "Luxury Feel", "Calming", "Chic"],
        "Luxury_Premium": ["Elegant", "Stylish", "Modern", "Sleek", "Luxury", "High-End", "Exclusive", "Sophisticated", "Premium Quality"],
        "High_Quality": ["Durable", "High-Quality", "Long-Lasting", "Reliable", "Heavy Duty", "Sturdy", "Waterproof", "Scratch-Resistant"],
        "Ease_Convenience": ["Easy to Use", "Hassle-Free", "User-Friendly", "One-Touch", "Adjustable", "Portable", "Versatile", "Lightweight"]
    }

    def generate_listing(self, input_data: dict) -> dict:
        try:
            logger.info("Starting generate_listing with input: %s", input_data)
            if not input_data["title"]:
                raise ValueError("Tiêu đề sản phẩm là bắt buộc")
            
            prompt = f"""
# CHUYÊN GIA TỐI ƯU LISTING SẢN PHẨM AMAZON

## DỮ LIỆU ĐẦU VÀO
- Tiêu đề gốc: {input_data['title']}
- Mô tả sản phẩm ban đầu: {input_data['product_description']}

## BƯỚC 1: PHÂN TÍCH VÀ TRÍCH XUẤT THÔNG TIN
Từ tiêu đề và mô tả sản phẩm trên, hãy cẩn thận đọc và trích xuất các thông tin sau:

### A. THUỘC TÍNH VẬT LÝ (tìm và ghi chép từ mô tả)
- **Màu sắc:** (đỏ, xanh, đen, trắng, etc.)
- **Kích thước:** (chiều dài x rộng x cao, size S/M/L, etc.)
- **Trọng lượng:** (gram, kg, etc.)
- **Chất liệu:** (nhựa, kim loại, vải, da, etc.)
- **Xuất xứ/thương hiệu:** (Made in Vietnam, Nike, Samsung, etc.)

### B. ĐẶC ĐIỂM KỸ THUẬT (nếu có)
- **Thông số kỹ thuật:** (công suất, dung lượng, tốc độ, etc.)
- **Tính năng chính:** (chống nước, Bluetooth, cảm ứng, etc.)
- **Khả năng tương thích:** (iOS, Android, Windows, etc.)
- **Phụ kiện đi kèm:** (cáp sạc, hộp, túi đựng, etc.)

### C. THÔNG TIN SỬ DỤNG
- **Đối tượng sử dụng:** (nam, nữ, trẻ em, người lớn tuổi, etc.)
- **Mục đích sử dụng:** (công việc, thể thao, giải trí, etc.)
- **Tình huống sử dụng:** (trong nhà, ngoài trời, đi du lịch, etc.)
- **Độ khó sử dụng:** (đơn giản, cần hướng dẫn, chuyên nghiệp, etc.)

### D. GIÁ TRỊ & LỢI ÍCH
- **Giải quyết vấn đề gì:** (tiết kiệm thời gian, tăng hiệu quả, etc.)
- **Cải thiện cuộc sống như thế nào:** (sức khỏe, tiện lợi, tiết kiệm, etc.)
- **Điểm khác biệt so với sản phẩm tương tự:** (độ bền, thiết kế, giá cả, etc.)

### E. TỪ KHÓA QUAN TRỌNG
- **Từ khóa chính:** (tên sản phẩm, loại sản phẩm)
- **Từ khóa mô tả:** (màu sắc, kích thước, chất liệu)
- **Từ khóa lợi ích:** (tiện lợi, bền đẹp, chất lượng)
- **Từ khóa tìm kiếm phổ biến:** (dành cho nam/nữ, giá rẻ, chính hãng)

## BƯỚC 2: TẠO NỘI DUNG LISTING

Dựa trên thông tin đã trích xuất ở BƯỚC 1, hãy tạo nội dung theo các quy tắc sau:

### TITLE (Tiêu đề) - Tối đa 150 ký tự
**Cấu trúc:** [Thương hiệu] - [Loại sản phẩm] - [Đặc điểm chính] - [Lợi ích]

**Quy tắc:**
- Viết hoa chỉ chữ cái đầu từ quan trọng
- Từ khóa chính trong 80 ký tự đầu
- Dùng số thay vì chữ (3 thay vì ba)
- Ngôn ngữ tự nhiên, thu hút
- KHÔNG dùng: ALL CAPS, ký tự đặc biệt ($!#), "best seller"

### BULLET POINTS (5 điểm)
**Định dạng HTML bắt buộc:**
```html
<ul>
<li> Mô tả cụ thể lợi ích</li>
<li> Đặc điểm và ứng dụng</li>
<li> Vật liệu, độ bền, tiêu chuẩn</li>
<li> Dễ sử dụng, tiết kiệm thời gian</li>
<li> Bảo hành, hỗ trợ khách hàng</li>
</ul>
```

**Nguyên tắc:**
- Tập trung LỢI ÍCH, không chỉ liệt kê tính năng
- Trả lời trực tiếp thắc mắc của khách hàng
- Ngôn ngữ gần gũi, dễ hiểu
- Lồng ghép từ khóa tự nhiên
- Sử dụng từ khóa cảm xúc phù hợp từ các nhóm sau:
  * Gift Appeal: {self.Emotional_Keywords['Gift_Appeal']}
  * Comfort & Cozy: {self.Emotional_Keywords['Comfort_Cozy']}
  * Luxury & Premium: {self.Emotional_Keywords['Luxury_Premium']}
  * High Quality: {self.Emotional_Keywords['High_Quality']}
  * Ease & Convenience: {self.Emotional_Keywords['Ease_Convenience']}

### DESCRIPTION (Mô tả chi tiết)
**Cấu trúc HTML:**
```html
<h2>Giới thiệu sản phẩm</h2>
<p>Mô tả tổng quan, lợi ích chính</p>

<h2>Tính năng nổi bật</h2>
<ul>
<li>Tính năng 1 với lợi ích cụ thể</li>
<li>Tính năng 2 với ứng dụng thực tế</li>
</ul>

<h2>Thông tin kỹ thuật</h2>
<p>Chi tiết thông số, chất lượng, tiêu chuẩn</p>
```

## ĐỊNH DẠNG ĐỀ XUẤT JSON
Vui lòng trả về kết quả theo ĐÚNG định dạng JSON sau:

```json
{{
    "title": "Tiêu đề sản phẩm tối ưu SEO (tối đa 150 ký tự)",
    "bullet_points": "<ul><li>Nội dung</li><li>Nội dung</li><li>Nội dung</li><li>Nội dung</li><li>Nội dung</li></ul>",
    "description": "<h2>Giới thiệu sản phẩm</h2><p>Mô tả tổng quan...</p><h2>Tính năng nổi bật</h2><ul><li>Tính năng 1...</li><li>Tính năng 2...</li></ul><h2>Thông tin chi tiết</h2><p>Chi tiết kỹ thuật...</p>"
}}
```

**Ví dụ phân tích:**
- Input: "Áo thun nam cotton 100% màu đen size M, chất liệu thoáng mát"
- Trích xuất: Màu sắc (đen), Kích thước (M), Chất liệu (cotton 100%), Đối tượng (nam), Lợi ích (thoáng mát)

**LưU Ý:** Nếu thông tin nào không có trong mô tả, đừng bịa đặt. Chỉ sử dụng thông tin có sẵn.
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
            # Log only the first 100 characters to avoid encoding issues
            logger.info("OpenAI response content (first 100 chars): %s", content[:100] if content else "Empty response")
            
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
                required_fields = ["title", "bullet_points", "description"]
                for field in required_fields:
                    if field not in result:
                        raise ValueError(f"Thiếu trường bắt buộc: {field}")
                
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
        with ThreadPoolExecutor(max_workers=50) as executor:
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

@ecom_bp.route('/generate', methods=['POST'])
def generate_listing():
    try:
        data = request.get_json()
        result = generator.generate_listing(data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in generate_listing endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500 