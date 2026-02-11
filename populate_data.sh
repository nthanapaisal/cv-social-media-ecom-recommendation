#!/bin/bash

BASE_URL = "http://127.0.0.1:8000"

# Create product tests

curl -X POST "$BASE_URL/upload/product/" \
    -F "title = Classic Blue Denim Jacket" \
    -F "description = Premium quality denim jacket" \
    -F "category = fashion" \
    -F "target_demographic = women, age 16-50" \
    -F "image = @product_images/denim_jacket_female.webp" | jq .