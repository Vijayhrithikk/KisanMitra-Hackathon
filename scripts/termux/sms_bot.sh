#!/bin/bash
# KisanMitra SMS Bot - Shell Script for Termux
# Alternative to Python script

# Configuration
BACKEND_URL="http://YOUR_PC_IP:8001"
CHECK_INTERVAL=5
LAST_ID=""

echo "========================================"
echo "🌾 KisanMitra SMS Bot (Shell)"
echo "========================================"
echo "Backend: $BACKEND_URL"
echo ""

# Test backend connection
if curl -s "$BACKEND_URL/" > /dev/null 2>&1; then
    echo "✅ Backend connected"
else
    echo "❌ Cannot connect to backend"
    echo "Make sure: 1) Backend is running 2) IP is correct"
fi

echo ""
echo "Monitoring SMS... (Ctrl+C to stop)"
echo ""

while true; do
    # Get latest incoming SMS
    SMS=$(termux-sms-list -l 1 -t inbox 2>/dev/null)
    
    if [ -n "$SMS" ]; then
        # Parse SMS
        ID=$(echo "$SMS" | jq -r '.[0]._id // empty')
        SENDER=$(echo "$SMS" | jq -r '.[0].number // empty')
        BODY=$(echo "$SMS" | jq -r '.[0].body // empty')
        
        # Check if new message
        if [ -n "$ID" ] && [ "$ID" != "$LAST_ID" ]; then
            echo "📨 New SMS from $SENDER: $BODY"
            
            # Call backend
            RESPONSE=$(curl -s -X POST "$BACKEND_URL/sms-webhook" \
                -H "Content-Type: application/json" \
                -d "{\"message\": \"$BODY\", \"sender\": \"$SENDER\"}")
            
            # Extract response text
            REPLY=$(echo "$RESPONSE" | jq -r '.response // "Error"')
            
            # Send SMS reply
            termux-sms-send -n "$SENDER" "$REPLY"
            
            echo "✅ Reply sent"
            LAST_ID="$ID"
        fi
    fi
    
    sleep $CHECK_INTERVAL
done
