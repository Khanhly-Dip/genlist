# 📄 backend.md – Prompting cho Cursor AI (Amazon Ecom AI Service)

## 1. Mô tả dự án cơ bản

Dự án **Amazon Ecom AI Service** là một hệ thống backend được xây dựng bằng Flask nhằm cung cấp các API sử dụng mô hình AI để sinh nội dung cho sản phẩm bán hàng trên Amazon (title, bullet points, description). Hệ thống được tổ chức theo mô hình nhiều AI Agent, mỗi agent có một nhiệm vụ cụ thể, ví dụ: `ecom_agent`, `ictu_bot_agent`, `lecture_assistant_agent`.

## 2. Công nghệ sử dụng

* **Ngôn ngữ chính**: Python 3.12
* **Framework backend**: Flask 3 (mới nhất)
* **Xác thực**: JWT (Flask-JWT-Extended)
* **Tích hợp AI**: OpenAI SDK (gọi GPT API)
* **Validation**: Pydantic v2
* **Không sử dụng ORM**: Tối giản, tương tác MongoDB (nếu cần)

## 3. Khởi tạo cơ bản Flask App

** Tất cả sẽ nằm trong /backend

**Prompt dành cho Cursor AI:**

```
Tạo một Flask app đơn giản trong file `app.py`, sử dụng Flask 3 mới nhất, có cấu trúc hỗ trợ đăng ký các Blueprint sau này. Sử dụng biến môi trường `.env` để đọc các cấu hình cơ bản.
```

**Gợi ý thêm:**

* Sử dụng `python-dotenv` để load biến môi trường.
* Đảm bảo `app.py` có sẵn dòng để đăng ký blueprint từ agent.

## 4. Mô tả cấu trúc một AI Agent

Mỗi agent trong thư mục `/app/agents/{agent_name}` sẽ có cấu trúc chuẩn hóa như sau:

```
/app/agents/{agent_name}
  /schemas           # Khai báo input/output schema (Pydantic)
    request.py       # Input schema từ client (user input)
    response.py      # Schema dữ liệu trả về
  /services
    logic.py         # Hàm xử lý chính (gọi LLM, business logic)
  /routes
    endpoint.py      # Định nghĩa Flask Blueprint & API routes
  __init__.py        # Khởi tạo agent module
```

**Prompt dành cho Cursor AI:**

```
Khởi tạo một agent mới có tên là `ecom_agent`, tạo đầy đủ các thư mục và file như mô tả:
- /app/agents/ecom_agent/schemas/
- /app/agents/ecom_agent/schemas/
- /app/agents/ecom_agent/services/
- /app/agents/ecom_agent/routes/ecom.py
- /app/agents/ecom_agent/__init__.py
```