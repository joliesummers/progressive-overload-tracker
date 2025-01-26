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

echo "Starting Progressive Overload API Test Plan..."
echo "============================================"

# Test 1: Create new user
echo "Test 1: Creating new user"
USER_ID=1  # For testing, use a hardcoded user ID
echo "Using hardcoded user ID: $USER_ID"
print_result "Create User"

# Test 2: Starting new workout session
echo "Test 2: Starting new workout session"
SESSION_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/workout/start" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": $USER_ID}")
echo "Session Response: $SESSION_RESPONSE"
SESSION_ID=$(echo "$SESSION_RESPONSE" | jq -r '.id')
if [ -z "$SESSION_ID" ] || [ "$SESSION_ID" = "null" ]; then
    echo "Error: No session ID received from start_workout"
    exit 1
fi
echo "Session ID: $SESSION_ID"
print_result "Start Workout Session"

# Test 3: Process workout with arrays
echo "Test 3: Processing workout with arrays"
echo "Using session ID: $SESSION_ID"
REQUEST_BODY="{\"session_id\": $SESSION_ID, \"workout_text\": \"Bench Press: 3 sets - Set 1: 135lbs x 10 reps, Set 2: 155lbs x 8 reps, Set 3: 175lbs x 6 reps. RPE: 8, Rest: 90 seconds\"}"
echo "Request body: $REQUEST_BODY"

WORKOUT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/workout/process" \
  -H "Content-Type: application/json" \
  -d "$REQUEST_BODY")
echo "Raw Workout Response: $WORKOUT_RESPONSE"

# Extract exercise ID from response
EXERCISE_ID=$(echo "$WORKOUT_RESPONSE" | jq -r '.id')
if [ -z "$EXERCISE_ID" ] || [ "$EXERCISE_ID" = "null" ]; then
    echo "Error: No exercise ID received from process_workout"
    exit 1
fi
print_result "Process Workout"

# Test 4: Get exercise details
echo "Test 4: Getting exercise details"
EXERCISE_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/workout/exercises/$EXERCISE_ID" \
  -H "Content-Type: application/json")
echo "Raw Exercise Response: $EXERCISE_RESPONSE"
echo "Exercise ID: $EXERCISE_ID"
print_result "Get Exercise Details"

# Test 5: Verify array fields
echo "Test 5: Verifying array fields"
EXERCISE_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/exercise/$EXERCISE_ID")
echo "Raw Exercise Response: $EXERCISE_RESPONSE"

# Extract arrays
REPS_ARRAY=$(echo "$EXERCISE_RESPONSE" | jq -c '.reps')
WEIGHT_ARRAY=$(echo "$EXERCISE_RESPONSE" | jq -c '.weight')
echo "Reps Array: $REPS_ARRAY"
echo "Weight Array: $WEIGHT_ARRAY"

# Expected arrays
EXPECTED_REPS='[10,8,6]'
EXPECTED_WEIGHTS='[135,155,175]'

# Compare arrays
if [ "$REPS_ARRAY" = "$EXPECTED_REPS" ]; then
    echo -e "${GREEN}✓ Reps array matches expected: $REPS_ARRAY${NC}"
else
    echo -e "${RED}✗ Reps array mismatch. Expected: $EXPECTED_REPS, Got: $REPS_ARRAY${NC}"
    TEST_FAILED=1
fi

if [ "$WEIGHT_ARRAY" = "$EXPECTED_WEIGHTS" ]; then
    echo -e "${GREEN}✓ Weight array matches expected: $WEIGHT_ARRAY${NC}"
else
    echo -e "${RED}✗ Weight array mismatch. Expected: $EXPECTED_WEIGHTS, Got: $WEIGHT_ARRAY${NC}"
    TEST_FAILED=1
fi

[ "$TEST_FAILED" != "1" ]
print_result "Array Field Verification"

# Test 6: End workout session
echo "Test 6: Ending workout session"
END_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/workout/end" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": $SESSION_ID}")
print_result "End Workout Session"

# Test 7: Get workout summary
echo "Test 7: Getting workout summary"
SUMMARY_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/workout/$SESSION_ID/summary" \
  -H "Content-Type: application/json")
print_result "Get Workout Summary"

echo "============================================"
echo "Test plan execution completed"
