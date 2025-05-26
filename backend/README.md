# Amazon Ecom AI Service Backend

This is the backend service for the Amazon Ecom AI Service, which provides AI-powered content generation for Amazon product listings.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the backend directory with the following content:
```
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
OPENAI_API_KEY=your-openai-api-key-here
```

4. Run the application:
```bash
python app.py
```

## API Endpoints

### Health Check
- `GET /health`
  - Returns the health status of the service

### Ecom Agent
- `POST /api/ecom/generate`
  - Generates product content (title, bullet points, description)
  - Request body example:
    ```json
    {
      "product": {
        "product_name": "Coffee Maker",
        "category": "Kitchen Appliances",
        "keywords": ["drip coffee", "programmable", "10-cup"],
        "target_marketplace": "US"
      },
      "generate_title": true,
      "generate_bullets": true,
      "generate_description": true
    }
    ```

## Project Structure

```
backend/
├── app/
│   └── agents/
│       └── ecom_agent/
│           ├── schemas/
│           │   ├── request.py
│           │   └── response.py
│           ├── services/
│           │   └── logic.py
│           ├── routes/
│           │   └── ecom.py
│           └── __init__.py
├── app.py
├── requirements.txt
└── .env
``` 