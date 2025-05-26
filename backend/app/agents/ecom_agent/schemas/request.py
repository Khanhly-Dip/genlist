from pydantic import BaseModel, Field
from typing import List, Optional

class ProductInput(BaseModel):
    title: str = Field(..., description="Tiêu đề sản phẩm")
    product_type: str = Field(..., description="Loại sản phẩm")
    color: str = Field(..., description="Màu sắc")
    size: str = Field(..., description="Kích thước")
    weight: str = Field(..., description="Trọng lượng")
    material_type: str = Field(..., description="Chất liệu")
    generic_keywords: List[str] = Field(..., description="Danh sách từ khóa")
    product_description: str = Field(..., description="Mô tả sản phẩm")

class BatchProductRequest(BaseModel):
    products: List[ProductInput] = Field(..., description="Danh sách sản phẩm cần tạo nội dung") 