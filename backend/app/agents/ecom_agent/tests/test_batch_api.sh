#!/bin/bash

# API endpoint
API_URL="http://localhost:5000/api/ecom/batch/process-batch"

# Test data with proper UTF-8 encoding
TEST_DATA='[
  {
    "title": "Ao thun nam cotton 100% mau den size M",
    "product_description": "Ao thun nam cotton 100% mau den size M, chat lieu thoang mat, tham hut mo hoi tot, phu hop cho mua he"
  },
  {
    "title": "Quan jean nam slim fit mau xanh",
    "product_description": "Quan jean nam slim fit mau xanh, chat lieu cotton denim cao cap, co gian 4 chieu, kieu dang hien dai"
  }
]'

# Test 1: Basic batch processing
echo "Test 1: Basic batch processing"
curl -X POST \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "$TEST_DATA" \
  "$API_URL"

echo -e "\n\n"

# Test 2: Empty title (error case)
echo "Test 2: Empty title (error case)"
ERROR_DATA='[
  {
    "title": "",
    "product_description": "Test description"
  },
  {
    "title": "Valid product",
    "product_description": "Valid description"
  }
]'

curl -X POST \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "$ERROR_DATA" \
  "$API_URL"

echo -e "\n\n"

# Test 3: Large batch (50 products)
echo "Test 3: Large batch (50 products)"
LARGE_BATCH='['
for i in {1..50}
do
  if [ $i -gt 1 ]; then
    LARGE_BATCH+=","
  fi
  LARGE_BATCH+="{\"title\":\"Test Product $i\",\"product_description\":\"Test Description $i\"}"
done
LARGE_BATCH+="]"

curl -X POST \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "$LARGE_BATCH" \
  "$API_URL"

echo -e "\n\n"

# Test 4: Invalid JSON
echo "Test 4: Invalid JSON"
curl -X POST \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "invalid json" \
  "$API_URL"

echo -e "\n\n"

# Test 5: Missing required fields
echo "Test 5: Missing required fields"
INVALID_DATA='[
  {
    "title": "Missing description"
  },
  {
    "product_description": "Missing title"
  }
]'

curl -X POST \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "$INVALID_DATA" \
  "$API_URL" 