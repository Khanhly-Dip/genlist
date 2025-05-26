from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class FeedProduct(BaseModel):
    item_type: str = Field(..., description="Loại sản phẩm")
    standard_price: str = Field(..., description="Giá sản phẩm")
    color: str = Field(..., description="Màu sắc")
    size: str = Field(..., description="Kích thước")
    material_type: str = Field(..., description="Chất liệu")
    generic_keywords: str = Field(..., description="Từ khóa chung")

class GeneratedContent(BaseModel):
    title: str = Field(..., description="Tiêu đề sản phẩm đã tối ưu")
    feed_product: FeedProduct = Field(..., description="Thông tin sản phẩm")
    short_description: str = Field(..., description="Mô tả ngắn với bullet points")
    description: str = Field(..., description="Mô tả chi tiết HTML")

class BatchContentGenerationResponse(BaseModel):
    results: List[Dict[str, Any]] = Field(..., description="Danh sách kết quả tạo nội dung") 