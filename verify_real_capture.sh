#!/bin/bash
# Verify Real Packet Capture (No Synthetic Data)

echo "🔍 Verifying Real Packet Capture Status"
echo "========================================"
echo ""

cd "$(dirname "$0")"

# 1. Check system status
echo "1️⃣  System Status:"
STATUS=$(curl -s http://localhost:5000/api/system/status)
CAPTURING=$(echo "$STATUS" | python3 -c "import sys,json; print(json.load(sys.stdin)['is_capturing_packets'])")
INJECT_RATE=$(echo "$STATUS" | python3 -c "import sys,json; print(json.load(sys.stdin)['process_info']['inject_rate'])")
RECENT=$(echo "$STATUS" | python3 -c "import sys,json; print(json.load(sys.stdin)['recent_packets_30s'])")

echo "   Capturing packets: $CAPTURING"
echo "   Inject rate: $INJECT_RATE (0.0 = real packets only)"
echo "   Packets (last 30s): $RECENT"
echo ""

# 2. Check for synthetic IPs (10.x.x.x)
echo "2️⃣  Checking for synthetic IPs (10.x.x.x):"
SYNTHETIC_COUNT=$(sqlite3 data/detections.db "SELECT COUNT(*) FROM detections WHERE source_ip LIKE '10.%' OR dest_ip LIKE '10.%';" 2>/dev/null)
echo "   Synthetic packets found: $SYNTHETIC_COUNT"

if [ "$SYNTHETIC_COUNT" -gt 0 ]; then
    echo "   ⚠️  WARNING: Found synthetic packets in database"
    echo "   These may be from previous runs with inject-rate > 0"
else
    echo "   ✅ No synthetic packets found"
fi
echo ""

# 3. Show recent real IPs
echo "3️⃣  Recent packet sources (should be real IPs):"
sqlite3 data/detections.db "SELECT DISTINCT source_ip, COUNT(*) as count FROM (SELECT * FROM detections ORDER BY id DESC LIMIT 50) GROUP BY source_ip ORDER BY count DESC LIMIT 5;" 2>/dev/null | while IFS='|' read ip count; do
    if [[ $ip == 10.* ]]; then
        echo "   ❌ $ip ($count) - SYNTHETIC"
    elif [[ $ip == 192.168.* ]]; then
        echo "   ✅ $ip ($count) - Local network (your computer/router)"
    else
        echo "   ✅ $ip ($count) - Public IP (real internet traffic)"
    fi
done
echo ""

# 4. Check detection process
echo "4️⃣  Detection Process:"
PROCESS=$(ps aux | grep "anomaly_detection/main.py" | grep -v grep | head -1)
if [ -n "$PROCESS" ]; then
    echo "   ✅ Detection process is running"
    echo "$PROCESS" | grep -o '\--inject-rate [0-9.]*' | while read -r line; do
        echo "   $line"
    done
    echo "$PROCESS" | grep -o '\--backend [a-z]*' | while read -r line; do
        echo "   $line"
    done
else
    echo "   ❌ Detection process not running"
fi
echo ""

# 5. Verify WiFi status
echo "5️⃣  Network Interface:"
if ip link show wlo1 2>/dev/null | grep -q "state UP"; then
    IP=$(ip addr show wlo1 | grep "inet " | awk '{print $2}')
    echo "   ✅ wlo1 is UP with IP: $IP"
else
    echo "   ❌ wlo1 is DOWN"
fi
echo ""

echo "========================================"
if [ "$INJECT_RATE" == "0.0" ] && [ "$CAPTURING" == "True" ] && [ "$SYNTHETIC_COUNT" -eq 0 ]; then
    echo "✅ VERIFIED: Capturing REAL packets only!"
elif [ "$INJECT_RATE" == "0.0" ] && [ "$CAPTURING" == "True" ]; then
    echo "✅ Capturing real packets (old synthetic data in DB)"
elif [ "$INJECT_RATE" != "0.0" ]; then
    echo "⚠️  WARNING: inject-rate is $INJECT_RATE (synthetic mode)"
else
    echo "❌ Not capturing packets"
fi
echo "========================================"
