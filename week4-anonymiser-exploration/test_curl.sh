#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# API base URL
BASE_URL="http://localhost:9000"

echo -e "${BLUE}Testing Anonymiser API with curl${NC}\n"

# Test 1: Health Check
echo -e "${BLUE}1. Testing Health Check...${NC}"
curl -s "$BASE_URL/health" | jq .
echo -e "\n"

# Test 2: Anonymise single text
echo -e "${BLUE}2. Testing Single Text Anonymisation...${NC}"
RESPONSE=$(curl -s -X POST "$BASE_URL/anonymise" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "John Smith works at Acme Corp. His email is john.smith@example.com and phone is 555-123-4567."
  }')

echo "$RESPONSE" | jq .
SESSION_ID=$(echo "$RESPONSE" | jq -r .session_id)
ANONYMISED_TEXT=$(echo "$RESPONSE" | jq -r .anonymised_text)

echo -e "${GREEN}Session ID: $SESSION_ID${NC}"
echo -e "${GREEN}Anonymised: $ANONYMISED_TEXT${NC}\n"

# Test 3: De-anonymise the text
echo -e "${BLUE}3. Testing De-anonymisation...${NC}"
DEANON_RESPONSE=$(curl -s -X POST "$BASE_URL/deanonymise" \
  -H "Content-Type: application/json" \
  -d "{
    \"anonymised_text\": \"$ANONYMISED_TEXT\",
    \"session_id\": \"$SESSION_ID\"
  }")

echo "$DEANON_RESPONSE" | jq .
ORIGINAL_TEXT=$(echo "$DEANON_RESPONSE" | jq -r .original_text)
echo -e "${GREEN}Original: $ORIGINAL_TEXT${NC}\n"

# Test 4: Batch anonymisation
echo -e "${BLUE}4. Testing Batch Anonymisation...${NC}"
BATCH_RESPONSE=$(curl -s -X POST "$BASE_URL/anonymise_batch" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Customer John called from 555-111-2222 about his account.",
      "Jane from Acme Corp requested a callback at jane.doe@acme.com.",
      "Dr. Smith visited on 2024-01-15 at 123 Main Street, New York."
    ]
  }')

echo "$BATCH_RESPONSE" | jq .
BATCH_SESSION_ID=$(echo "$BATCH_RESPONSE" | jq -r .session_id)
echo -e "${GREEN}Batch Session ID: $BATCH_SESSION_ID${NC}\n"

# Test 5: Anonymise with custom names
echo -e "${BLUE}5. Testing Anonymisation with Custom Names...${NC}"
CUSTOM_RESPONSE=$(curl -s -X POST "$BASE_URL/anonymise" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Please contact MegaCorp CEO John Doe at their headquarters.",
    "specific_names": ["MegaCorp", "John Doe"]
  }')

echo "$CUSTOM_RESPONSE" | jq .
echo -e "\n"

# Test 6: Test match de-anonymisation
echo -e "${BLUE}6. Testing Match De-anonymisation...${NC}"
# First create some anonymised text
MATCH_ANON=$(curl -s -X POST "$BASE_URL/anonymise" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Contact support@company.com for assistance"
  }')

MATCH_SESSION=$(echo "$MATCH_ANON" | jq -r .session_id)
MATCH_TEXT=$(echo "$MATCH_ANON" | jq -r .anonymised_text)

# Now de-anonymise as a match result
MATCH_DEANON=$(curl -s -X POST "$BASE_URL/deanonymise-match" \
  -H "Content-Type: application/json" \
  -d "{
    \"match_result\": {
      \"text\": \"$MATCH_TEXT\",
      \"score\": 0.95,
      \"metadata\": {\"source\": \"test\"}
    },
    \"session_id\": \"$MATCH_SESSION\"
  }")

echo "$MATCH_DEANON" | jq .
echo -e "\n"

# Test 7: Clean up sessions
echo -e "${BLUE}7. Testing Session Cleanup...${NC}"
curl -s -X DELETE "$BASE_URL/sessions/$SESSION_ID" | jq .
echo -e "\n"

# Final health check
echo -e "${BLUE}8. Final Health Check...${NC}"
curl -s "$BASE_URL/health" | jq .

echo -e "\n${GREEN}✅ All curl tests completed!${NC}"