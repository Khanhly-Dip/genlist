import requests
import json

def test_generate_endpoint():
    url = "http://localhost:5001/api/ecom/generate"
    
    # Sample product data
    data = {
        "title": "Premium Cotton T-Shirt",
        "product_type": "Clothing",
        "color": "Black",
        "size": "M",
        "weight": "150g",
        "material_type": "100% Cotton",
        "generic_keywords": ["tshirt", "cotton", "casual", "comfortable"],
        "product_description": "High-quality cotton t-shirt perfect for everyday wear. Features a comfortable fit and durable construction."
    }
    
    # Make POST request
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_generate_endpoint() 