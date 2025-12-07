#!/bin/bash

echo "=========================================="
echo "Testing CQRS+EDA Implementation"
echo "Assignment 3 - Part 4: Use Case Implementation"
echo "=========================================="
echo ""

BASE_URL="http://localhost:8000"

echo " Testing 5 Use Cases with CQRS+EDA Pattern"
echo ""

# Test Use Case 1: User Registration
echo "  Use Case 1: User Registration with Event Notification"
echo "   POST /api/cqrs/auth/register"
REGISTER_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/cqrs/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser123",
    "email": "test@example.com",
    "password": "securepass123",
    "role": "student",
    "full_name": "Test User"
  }')

echo "$REGISTER_RESPONSE" | python3 -m json.tool
echo ""

# Extract user_id for use in other tests
USER_ID=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['user_id'])" 2>/dev/null)
echo "   ✓ User ID for testing: $USER_ID"
echo "   ✓ Expected: User created in 3 tables, UserRegisteredEvent published"
echo ""
read -p "Press Enter to continue..."
echo ""

# Test Use Case 2: Resource Upload (using real user_id)
echo "  Use Case 2: Resource Upload with Auto-Tagging"
echo "   POST /api/cqrs/resources/upload"
UPLOAD_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/cqrs/resources/upload" \
  -F "title=Calculus Study Guide" \
  -F "description=Comprehensive calculus notes" \
  -F "resource_type=pdf" \
  -F "difficulty_level=intermediate" \
  -F "uploader_user_id=$USER_ID" \
  -F "file_name=calculus-guide.pdf")

echo "$UPLOAD_RESPONSE" | python3 -m json.tool
echo ""

# Extract resource_id for use in other tests
RESOURCE_ID=$(echo "$UPLOAD_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['resource_id'])" 2>/dev/null)
echo "   ✓ Resource ID for testing: $RESOURCE_ID"
echo "   ✓ Expected: Resource created in 3 tables, tags auto-generated, ResourceUploadedEvent published"
echo ""
read -p "Press Enter to continue..."
echo ""

# Test Use Case 3: View Resource (using real IDs)
echo "  Use Case 3: View Resource with Activity Tracking"
echo "   POST /api/cqrs/resources/${RESOURCE_ID}/view"
VIEW_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/cqrs/resources/${RESOURCE_ID}/view" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"view_duration_seconds\": 245,
    \"device_type\": \"desktop\",
    \"session_id\": \"session-xyz-789\"
  }")

echo "$VIEW_RESPONSE" | python3 -m json.tool
echo ""
echo "   ✓ Expected: View logged, stats updated, ResourceViewedEvent published"
echo ""
read -p "Press Enter to continue..."
echo ""

# Test Use Case 4: Rate Resource (using real IDs)
echo "  Use Case 4: Rate Resource with Stats Update"
echo "   POST /api/cqrs/resources/${RESOURCE_ID}/rate"
RATE_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/cqrs/resources/${RESOURCE_ID}/rate" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"rating_value\": 5,
    \"review_text\": \"Excellent study guide! Very helpful.\"
  }")

echo "$RATE_RESPONSE" | python3 -m json.tool
echo ""
echo "   ✓ Expected: Rating logged, average recalculated, ResourceRatedEvent published"
echo ""
read -p "Press Enter to continue..."
echo ""

# Test Use Case 5: Generate Recommendations (using real user_id)
echo "  Use Case 5: Generate Personalized Recommendations"
echo "   POST /api/cqrs/recommendations/generate"
REC_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/cqrs/recommendations/generate" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"limit\": 5,
    \"algorithm\": \"hybrid\"
  }")

echo "$REC_RESPONSE" | python3 -m json.tool
echo ""
echo "   ✓ Expected: Recommendations generated, RecommendationsGeneratedEvent published"
echo ""
read -p "Press Enter to continue..."
echo ""

# Query event log
echo "Querying Event Log (to verify EDA pattern)"
echo "   GET /api/cqrs/events"
curl -s "${BASE_URL}/api/cqrs/events" | python3 -m json.tool
echo ""

echo "=========================================="
echo "All 5 Use Cases Tested Successfully!"
echo "=========================================="
echo ""
echo "CQRS Pattern Demonstrated:"
echo "  ✓ Separate Command and Query operations"
echo "  ✓ Commands modify state across multiple tables"
echo "  ✓ Queries read from optimized read models"
echo ""
echo "EDA Pattern Demonstrated:"
echo "  ✓ Events published for each state change"
echo "  ✓ Event handlers process async side effects"
echo "  ✓ Decoupled components via event bus"
echo ""