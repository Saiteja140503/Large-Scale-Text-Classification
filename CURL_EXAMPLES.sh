#!/bin/bash

# Replace this with your actual API endpoint from CloudFormation outputs
API_URL="https://YOUR_API_ID.execute-api.YOUR_REGION.amazonaws.com/Prod/classify"

echo "==============================================="
echo "Text Classification API - Sample Requests"
echo "==============================================="
echo ""

# Example 1: Valid classification request
echo "Example 1: Valid Request - Graphics Topic"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I am looking for information about computer graphics and 3D rendering techniques for video game development."
  }' | jq .
echo ""
echo ""

# Example 2: Valid classification request - Medical
echo "Example 2: Valid Request - Medical Topic"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The patient presented with acute symptoms and was admitted to the hospital for further medical evaluation and treatment."
  }' | jq .
echo ""
echo ""

# Example 3: Valid classification request - Sports
echo "Example 3: Valid Request - Baseball Topic"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The baseball team won the championship yesterday with an amazing performance by their star pitcher who struck out fifteen batters."
  }' | jq .
echo ""
echo ""

# Example 4: Invalid - Missing text field
echo "Example 4: Invalid Request - Missing text field"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{}' | jq .
echo ""
echo ""

# Example 5: Invalid - Text too short
echo "Example 5: Invalid Request - Text too short"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Too short"
  }' | jq .
echo ""
echo ""

# Example 6: Invalid JSON
echo "Example 6: Invalid Request - Malformed JSON"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{invalid json}' | jq .
echo ""
echo ""

echo "==============================================="
echo "Expected Response Format:"
echo "==============================================="
echo '{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "category": "comp.graphics",
  "confidence": 0.9234,
  "input_length": 115
}'
