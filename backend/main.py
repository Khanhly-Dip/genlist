import json
from openai import OpenAI
from typing import Dict, List, Optional
from dotenv import load_dotenv
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load biến môi trường từ file .env
load_dotenv()

# Khởi tạo FastAPI app
app = FastAPI(title="Amazon Listing Generator API")

# Thêm cấu hình templates
templates = Jinja2Templates(directory="../frontend")

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://apiecom.teamexp.net",
        "https://ecom.teamexp.net",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model cho input data
class ProductInput(BaseModel):
    title: str
    product_type: str
    item_type_keyword: str
    color: str
    size: str
    weight: str
    material_type: str
    generic_keywords: List[str]
    product_description: str

class AmazonListingGenerator:
    def __init__(self):
        """Khởi tạo generator với API key từ file .env"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("Không tìm thấy OPENAI_API_KEY trong file .env")
        
        self.client = OpenAI(api_key=api_key)
        
        # Prompt template cho việc tạo nội dung SEO
        self.base_prompt = """Bạn là chuyên gia viết nội dung SEO cho sản phẩm của Amazon Seller Central. Hãy tạo content hấp dẫn, sáng tạo và chuẩn SEO từ thông tin sản phẩm dưới đây.

## THÔNG TIN SẢN PHẨM:
- Tiêu đề gốc: {title}
- Loại sản phẩm (Product Type): {product_type}
- Từ khóa phân loại (Item Type Keyword): {item_type_keyword}
- Màu sắc: {color}
- Kích thước (Size): {size}
- Trọng lượng phù hợp: {weight}
- Chất liệu: {material_type}
- Từ khóa chung (phân tách bằng dấu phẩy): {generic_keywords}
- Mô tả sản phẩm ban đầu: {product_description}

## YÊU CẦU:
1. **Tiêu đề sản phẩm (SEO Title)**: Viết tiêu đề dài 100–200 ký tự, chèn từ khóa chính tự nhiên, hấp dẫn người mua, tạo được thu hút ngay khi đọc, có thể trích xuất thêm từ mô tả sản phẩm ban đầu vào tiêu đề và thân thiện với công cụ tìm kiếm.
2. **Bullet points (Tính năng nổi bật)**: Viết 5 gạch đầu dòng giới thiệu về các đặc điểm, nhấn mạnh lợi ích,phong cách ngôn từ tự nhiên, đặc điểm nổi bật và lý do nên chọn sản phẩm.
3. **Mô tả chi tiết (HTML Description)**: Viết đoạn mô tả 300–500 từ, chia cấu trúc rõ ràng bằng thẻ HTML (h2, p, strong, ul/li). Nội dung cần dễ đọc, giàu tính thuyết phục, hỗ trợ SEO và voice search.
4. generic_keywords thì là truyền chữ với dấu chấm phẩy
5. Có thể dùng các từ đồng nghĩa để tạo nên giong văn tự nhiên, không lặp lại từ khóa quá nhiều lần.

## ĐỊNH DẠNG ĐẦU RA:
Trả về đúng định dạng JSON bên dưới:

{{
    "title": "Tiêu đề sản phẩm tối ưu SEO",
    "feed_product": {{
        "item_type": "{product_type}",
        "standard_price": "Liên hệ",
        "color": "{color}",
        "size": "{size}",
        "material_type": "{material_type}",
        "generic_keywords": "{generic_keywords}"
    }},
    "short_description": "<ul><li>Bullet point 1</li><li>Bullet point 2</li><li>...</li></ul>",
    "description": "<h2>Giới thiệu sản phẩm</h2><p>...</p><h2>Thông tin chi tiết</h2><ul><li>...</li></ul><p>...</p>"
}}
"""

    def _format_prompt(self, input_data: Dict) -> str:
        """Format prompt template với dữ liệu đầu vào"""
        return self.base_prompt.format(
            title=input_data["title"],
            product_type=input_data["product_type"],
            item_type_keyword=input_data["item_type_keyword"],
            color=input_data["color"],
            size=input_data["size"],
            weight=input_data["weight"],
            material_type=input_data["material_type"],
            generic_keywords=json.dumps(input_data["generic_keywords"]),
            product_description=input_data["product_description"]
        )

    def generate_listing(self, input_data: Dict) -> Dict:
        """Tạo nội dung listing sử dụng LLM"""
        try:
            # Kiểm tra đầu vào cơ bản
            if not input_data["title"]:
                raise ValueError("Tiêu đề sản phẩm là bắt buộc")
            
            # Format prompt
            prompt = self._format_prompt(input_data)
            logger.info("Generated prompt: %s", prompt)

            # Gọi API của OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Bạn là một chuyên gia tạo nội dung cho Amazon Seller Central. Hãy tạo nội dung tối ưu SEO và hấp dẫn người mua. Luôn trả về kết quả dưới dạng JSON hợp lệ."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            # Parse kết quả từ LLM
            content = response.choices[0].message.content
            logger.info("Raw response from OpenAI: %s", content)

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

# Khởi tạo generator
generator = AmazonListingGenerator()

@app.post("/generate-listing")
async def generate_listing(input_data: ProductInput):
    """
    Tạo nội dung listing cho sản phẩm Amazon
    
    - **title**: Tiêu đề cho sản phẩm
    - **product_type**: Loại sản phẩm
    - **item_type_keyword**: Item Type Keyword
    - **color**: Màu sắc của sản phẩm
    - **size**: Kích thước của sản phẩm
    - **weight**: Trọng lượng của sản phẩm
    - **material_type**: Loại chất liệu
    - **generic_keywords**: Các từ khóa cho sản phẩm
    - **product_description**: Mô tả ngắn về sản phẩm
    """
    try:
        logger.info("Received input data: %s", input_data.model_dump())
        result = generator.generate_listing(input_data.model_dump())
        if "error" in result:
            logger.error("Generation error: %s", result["error"])
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        logger.error("API error: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# Lấy đường dẫn tuyệt đối đến thư mục frontend
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

# Mount thư mục frontend để phục vụ file tĩnh
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
async def root():
    """Chuyển hướng đến giao diện web"""
    return RedirectResponse(url="/web")

@app.get("/web")
async def web_interface(request: Request):
    """Phục vụ giao diện web từ thư mục frontend"""
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)