#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BLUE='\033[0;34m'

API_URL="http://localhost:8000"
PYTHON_CMD="venv/bin/python"

# Function to print section headers
print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

# Function to check if the previous command was successful
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Success${NC}"
    else
        echo -e "${RED}Failed${NC}"
        exit 1
    fi
}

# Function to pretty print JSON
pretty_print_json() {
    echo "$1" | $PYTHON_CMD -m json.tool || echo "$1"
}

# Test exercises
EXERCISES=(
    "3 sets of barbell squats with 225 lbs"
    "4 sets of bench press at 185 lbs"
    "3 sets of deadlifts at 275 lbs"
)

# Create a workout session
print_header "Creating workout session"
SESSION_RESPONSE=$(curl -s -X POST "${API_URL}/workout/start" \
    -H "Content-Type: application/json" \
    -d '{"user_id": 1}')
check_status

echo "Session response:"
pretty_print_json "$SESSION_RESPONSE"

# Extract session ID
SESSION_ID=$(echo $SESSION_RESPONSE | grep -o '"id":[0-9]*' | cut -d':' -f2)
if [ -z "$SESSION_ID" ]; then
    echo -e "${RED}Failed to get session ID${NC}"
    exit 1
fi
echo "Created session ID: $SESSION_ID"

# Process each exercise
for exercise in "${EXERCISES[@]}"; do
    print_header "Analyzing exercise: $exercise"
    
    # Extract exercise name for storage
    EXERCISE_NAME=$(echo $exercise | sed -E 's/[0-9]+ sets of ([^with]*)with.*/\1/' | xargs)
    
    # Send to chat endpoint
    RESPONSE=$(curl -s -X POST "${API_URL}/chat" \
        -H "Content-Type: application/json" \
        -d "{
            \"message\": \"$exercise\",
            \"session_id\": $SESSION_ID,
            \"exercise_name\": \"$EXERCISE_NAME\"
        }")
    check_status
    
    echo "Response:"
    pretty_print_json "$RESPONSE"
done

# End workout session
print_header "Ending workout session"
END_RESPONSE=$(curl -s -X POST "${API_URL}/workout/end/$SESSION_ID")
check_status
echo "End session response:"
pretty_print_json "$END_RESPONSE"

# Check analytics
print_header "Checking muscle tracking data"
TRACKING_DATA=$(curl -s "${API_URL}/analytics/muscle-tracking")
echo "Muscle tracking data:"
pretty_print_json "$TRACKING_DATA"

print_header "Checking muscle volume data"
VOLUME_DATA=$(curl -s "${API_URL}/analytics/muscle-volume-data")
echo "Muscle volume data:"
pretty_print_json "$VOLUME_DATA"
