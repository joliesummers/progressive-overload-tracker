#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BLUE='\033[0;34m'

API_URL="http://localhost:8000"

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

# Test exercises
print_header "Analyzing exercises with Bedrock agent"

# Test multiple exercises to build up data
exercises=(
    "3 sets of barbell squats with 225 lbs"
    "4 sets of bench press with 185 lbs"
    "3 sets of deadlifts with 315 lbs"
    "4 sets of shoulder press with 135 lbs"
)

for exercise in "${exercises[@]}"; do
    echo "Testing: $exercise"
    RESPONSE=$(curl -s -X POST "${API_URL}/chat" \
        -H "Content-Type: application/json" \
        -d "{
            \"message\": \"$exercise\"
        }")
    check_status
    echo "Agent Response:"
    echo "$RESPONSE" | python3 -m json.tool || echo "$RESPONSE"
    echo -e "\n"
    sleep 2  # Add a small delay between requests
done

print_header "Checking analytics endpoints"
echo "Muscle tracking data:"
curl -s "${API_URL}/analytics/muscle-tracking" | python3 -m json.tool || echo "Failed to get muscle tracking data"

echo -e "\nMuscle volume data:"
curl -s "${API_URL}/analytics/muscle-volume-data" | python3 -m json.tool || echo "Failed to get muscle volume data"
