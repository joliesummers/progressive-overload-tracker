#!/bin/bash

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Helper function to print test results
print_result() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1 passed${NC}"
    else
        echo -e "${RED}✗ $1 failed${NC}"
    fi
    echo "----------------------------------------"
}

echo "Starting End-to-End Chat to Summary Test..."
echo "============================================"

# Test 1: Send chat message to start workout
echo "Test 1: Sending chat message to start workout"
CHAT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I just finished my workout. I did bench press: 3 sets - Set 1: 135lbs x 10 reps, Set 2: 155lbs x 8 reps, Set 3: 175lbs x 6 reps. RPE was 8, and I rested 90 seconds between sets."
  }')
echo "Chat Response: $CHAT_RESPONSE"

# Extract session ID from chat response
SESSION_ID=$(echo "$CHAT_RESPONSE" | jq -r '.session_id')
if [ -z "$SESSION_ID" ] || [ "$SESSION_ID" = "null" ]; then
    echo "Error: No session ID received from chat"
    exit 1
fi
echo "Session ID: $SESSION_ID"
print_result "Chat Processing"

# Test 2: Get exercise details
echo "Test 2: Getting exercise details"
EXERCISE_ID=$(echo "$CHAT_RESPONSE" | jq -r '.exercise_id')
if [ -z "$EXERCISE_ID" ] || [ "$EXERCISE_ID" = "null" ]; then
    echo "Error: No exercise ID received from chat"
    exit 1
fi

EXERCISE_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/workout/exercises/$EXERCISE_ID" \
  -H "Content-Type: application/json")
echo "Exercise Response: $EXERCISE_RESPONSE"

# Verify exercise data
REPS_ARRAY=$(echo "$EXERCISE_RESPONSE" | jq -r '.reps')
WEIGHT_ARRAY=$(echo "$EXERCISE_RESPONSE" | jq -r '.weight')

echo "Reps Array: $REPS_ARRAY"
echo "Weight Array: $WEIGHT_ARRAY"

if [[ $REPS_ARRAY == "[10,8,6]" ]]; then
    echo -e "${GREEN}✓ Reps array verified${NC}"
else
    echo -e "${RED}✗ Reps array incorrect: $REPS_ARRAY${NC}"
fi

if [[ $WEIGHT_ARRAY == "[135,155,175]" ]]; then
    echo -e "${GREEN}✓ Weight array verified${NC}"
else
    echo -e "${RED}✗ Weight array incorrect: $WEIGHT_ARRAY${NC}"
fi
print_result "Exercise Data Verification"

# Test 3: End workout session
echo "Test 3: Ending workout session"
END_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/workout/end" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": $SESSION_ID}")
print_result "End Workout Session"

# Test 4: Get workout summary
echo "Test 4: Getting workout summary"
SUMMARY_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/workout/$SESSION_ID/summary" \
  -H "Content-Type: application/json")
echo "Summary Response: $SUMMARY_RESPONSE"

# Verify summary data
TOTAL_VOLUME=$(echo "$SUMMARY_RESPONSE" | jq -r '.total_volume')
if [ -z "$TOTAL_VOLUME" ] || [ "$TOTAL_VOLUME" = "null" ] || [ "$TOTAL_VOLUME" = "0" ]; then
    echo -e "${RED}✗ Total volume not calculated${NC}"
else
    echo -e "${GREEN}✓ Total volume calculated: $TOTAL_VOLUME${NC}"
fi

EXERCISE_COUNT=$(echo "$SUMMARY_RESPONSE" | jq -r '.exercises | length')
if [ "$EXERCISE_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ Exercises found in summary: $EXERCISE_COUNT${NC}"
else
    echo -e "${RED}✗ No exercises in summary${NC}"
fi
print_result "Workout Summary"

echo "============================================"
echo "End-to-End test completed"
