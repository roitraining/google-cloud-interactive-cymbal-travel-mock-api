#!/bin/bash

# Configuration
BASE_URL="http://localhost:8080"
USER_ID="demo_user_$(date +%s)"

# Colors for pretty printing
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Cymbal Travel Mock API Demo ===${NC}"
echo "Target URL: $BASE_URL"
echo "Simulated User ID: $USER_ID"
echo "-----------------------------------"

# Helper function to pause
pause() {
    echo -e "${GREEN}Press ENTER to continue...${NC}"
    read -p "Press ENTER to continue..."
    echo ""
}

# Helper function to run a curl command.
run_api_call() {
    DESCRIPTION=$1
    METHOD=$2
    ENDPOINT=$3
    DATA=$4

    echo -e "${BLUE}Step: $DESCRIPTION${NC}"
    echo "Request: $METHOD $ENDPOINT"
    
    if [ "$METHOD" == "POST" ]; then
        echo "Payload: $DATA"
        response=$(curl -s -X POST "$BASE_URL$ENDPOINT" \
            -H "Content-Type: application/json" \
            -d "$DATA")
    else
        response=$(curl -s "$BASE_URL$ENDPOINT")
    fi

    echo "$response" > last_response.json
    
    if command -v jq &> /dev/null; then
        echo "$response" | jq .
    else
        echo "$response"
    fi
    
    pause
}

# 1. Initialize Inventory (Optional)
echo -ne "${BLUE}Do you want to reset the hotel and car inventory? [y/N]: ${NC}"
read RESET_CHOICE
RESET_CHOICE=${RESET_CHOICE:-N} # Default to No

if [[ "$RESET_CHOICE" =~ ^[Yy] ]]; then
    run_api_call "Initialize Inventory" "GET" "/api/save_inventory"
else
    echo "Skipping inventory reset."
fi

# 2. Search for Flights
run_api_call "Search Flights (SFO -> LHR)" "GET" \
    "/api/flights/search?origin=SFO&destination=LHR&date=2025-12-25"

# Extract ID if jq simulates
FLIGHT_ID=""
if command -v jq &> /dev/null; then
    FLIGHT_ID=$(cat last_response.json | jq -r '.[0].id // empty')
else
    # Fallback: grep for "id": "..." (fragile but okay for demo without jq)
    FLIGHT_ID=$(grep -o '"id": *"[^"]*"' last_response.json | head -1 | cut -d'"' -f4)
fi
echo "Captured Flight ID: $FLIGHT_ID"

# 3. Add Flight to Cart
if [ -n "$FLIGHT_ID" ] && [ "$FLIGHT_ID" != "null" ]; then
    run_api_call "Add Flight to Cart" "POST" "/api/cart/add" \
        "{\"user_id\": \"$USER_ID\", \"type\": \"flight\", \"item_id\": \"$FLIGHT_ID\", \"quantity\": 1}"
fi

# 4. Search Hotels
run_api_call "Search Hotels (Bali)" "GET" "/api/hotels/search?location=Bali"

# Extract Room ID (first hotel, first room)
ROOM_ID=""
if command -v jq &> /dev/null; then
    ROOM_ID=$(cat last_response.json | jq -r '.[0].rooms[0].id // empty')
else
    # Fallback grep for room id is hard because nested. Just skip if no jq for simplicity or try a simpler grep
    # This grep likely matches hotel ID first, which is wrong. 
    # Let's rely on jq for complex extractions.
    echo "jq not found, skipping precise extraction."
fi
echo "Captured Room ID: $ROOM_ID"

# 5. Add Hotel to Cart
if [ -n "$ROOM_ID" ] && [ "$ROOM_ID" != "null" ]; then
    run_api_call "Add Hotel Room to Cart" "POST" "/api/cart/add" \
        "{\"user_id\": \"$USER_ID\", \"type\": \"hotel\", \"item_id\": \"$ROOM_ID\", \"quantity\": 1, \"start_date\": \"2025-12-26\", \"end_date\": \"2025-12-30\"}"
fi

# 6. View Cart
run_api_call "View Cart" "GET" "/api/cart/$USER_ID"

# 7. Checkout
run_api_call "Checkout" "POST" "/api/cart/checkout" \
    "{\"user_id\": \"$USER_ID\"}"

# Cleanup
rm -f last_response.json
echo -e "${BLUE}=== Demo Complete ===${NC}"
