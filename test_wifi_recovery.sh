#!/bin/bash
# Test WiFi Auto-Recovery
# This script helps test that detection automatically pauses/resumes when WiFi goes down/up

echo "🧪 WiFi Auto-Recovery Test"
echo "========================================"
echo ""
echo "This test will help you verify that packet capture"
echo "automatically stops when WiFi goes down and resumes"
echo "when it comes back up."
echo ""
echo "Instructions:"
echo "  1. Make sure detection is running (./start_realtime_detection.sh)"
echo "  2. Watch the detection terminal output"
echo "  3. Turn WiFi OFF using your system settings"
echo "  4. You should see: '⚠️ Interface wlo1 went DOWN!'"
echo "  5. Wait a few seconds"
echo "  6. Turn WiFi back ON"
echo "  7. You should see: '✅ Interface wlo1 is back UP!'"
echo ""
echo "========================================"
echo ""

# Function to check interface status
check_interface() {
    if ip addr show wlo1 2>/dev/null | grep -q "state UP" && ip addr show wlo1 | grep -q "inet "; then
        echo "✅ wlo1 is UP with IP"
        ip addr show wlo1 | grep "inet " | awk '{print "   IP: " $2}'
        return 0
    else
        echo "❌ wlo1 is DOWN or no IP"
        return 1
    fi
}

# Function to check if capture is active
check_capture() {
    RECENT=$(curl -s http://localhost:5000/api/system/status 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['recent_packets_30s'])" 2>/dev/null)
    if [ -n "$RECENT" ] && [ "$RECENT" -gt 0 ]; then
        echo "✅ Capturing packets ($RECENT in last 30s)"
        return 0
    else
        echo "❌ Not capturing packets"
        return 1
    fi
}

echo "Current Status:"
echo "---------------"
check_interface
check_capture
echo ""

echo "========================================"
echo "Monitoring WiFi status (Ctrl+C to stop)..."
echo "========================================"
echo ""

PREVIOUS_STATE="unknown"

while true; do
    if ip addr show wlo1 2>/dev/null | grep -q "state UP" && ip addr show wlo1 | grep -q "inet "; then
        CURRENT_STATE="up"
        if [ "$PREVIOUS_STATE" = "down" ]; then
            echo "[$(date '+%H:%M:%S')] 🟢 WiFi came back UP!"
            echo "   Waiting for capture to resume..."
            sleep 5
            check_capture
        fi
    else
        CURRENT_STATE="down"
        if [ "$PREVIOUS_STATE" = "up" ]; then
            echo "[$(date '+%H:%M:%S')] 🔴 WiFi went DOWN!"
            echo "   Capture should pause..."
            sleep 5
            check_capture
        fi
    fi
    
    if [ "$PREVIOUS_STATE" != "$CURRENT_STATE" ] && [ "$PREVIOUS_STATE" != "unknown" ]; then
        echo ""
    fi
    
    PREVIOUS_STATE=$CURRENT_STATE
    sleep 3
done
