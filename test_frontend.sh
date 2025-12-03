#!/bin/bash
# Quick test to verify frontend data flow

echo "🔍 Testing Network Anomaly Detection Frontend Data Flow"
echo "========================================================"
echo ""

cd "$(dirname "$0")"

# 1. Check if database exists and has data
echo "1️⃣  Checking database..."
if [ -f "data/detections.db" ]; then
    DB_COUNT=$(sqlite3 data/detections.db "SELECT COUNT(*) FROM detections;" 2>/dev/null)
    echo "   ✅ Database found: $DB_COUNT detections"
else
    echo "   ❌ Database not found at data/detections.db"
    exit 1
fi

echo ""

# 2. Check if API is running
echo "2️⃣  Checking API server..."
if curl -s http://localhost:5000/api/detections/stats > /dev/null 2>&1; then
    echo "   ✅ API server is running on port 5000"
    
    # Get stats
    STATS=$(curl -s http://localhost:5000/api/detections/stats)
    TOTAL=$(echo $STATS | python3 -c "import sys, json; print(json.load(sys.stdin)['total_packets'])" 2>/dev/null)
    ANOMALIES=$(echo $STATS | python3 -c "import sys, json; print(json.load(sys.stdin)['total_anomalies'])" 2>/dev/null)
    echo "   📊 Total packets: $TOTAL"
    echo "   ⚠️  Anomalies: $ANOMALIES"
else
    echo "   ❌ API server not responding"
    echo "   💡 Run: ./start_advanced.sh"
    exit 1
fi

echo ""

# 3. Test recent detections endpoint
echo "3️⃣  Testing /api/detections/recent endpoint..."
RECENT=$(curl -s http://localhost:5000/api/detections/recent?limit=2)
if echo "$RECENT" | python3 -c "import sys, json; data=json.load(sys.stdin); exit(0 if isinstance(data, list) and len(data) > 0 else 1)" 2>/dev/null; then
    echo "   ✅ Recent detections endpoint working"
    echo "$RECENT" | python3 -m json.tool | head -20
else
    echo "   ❌ Recent detections endpoint failed"
    echo "   Response: $RECENT"
    exit 1
fi

echo ""

# 4. Check frontend
echo "4️⃣  Checking frontend..."
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "   ✅ Frontend is running on port 3000"
else
    echo "   ❌ Frontend not responding"
    echo "   💡 Run: ./start_advanced.sh"
    exit 1
fi

echo ""
echo "========================================================"
echo "✅ All checks passed!"
echo "========================================================"
echo ""
echo "📊 Open in browser: http://localhost:3000"
echo ""
echo "If frontend shows 'No data', try:"
echo "  1. Hard refresh browser (Ctrl+Shift+R)"
echo "  2. Open DevTools (F12) and check Console for errors"
echo "  3. Check Network tab for failed API calls"
echo ""
