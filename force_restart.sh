#!/bin/bash
# Force restart detection when it gets stuck

echo "🔄 Force Restarting Detection"
echo "=============================="
echo ""

cd "$(dirname "$0")"

# Find and kill detection process
echo "Stopping current detection process..."
PID=$(ps aux | grep "anomaly_detection/main.py" | grep -v grep | awk '{print $2}')

if [ -n "$PID" ]; then
    echo "Found detection process: PID $PID"
    kill $PID
    sleep 2
    
    # Force kill if still running
    if ps -p $PID > /dev/null 2>&1; then
        echo "Force killing..."
        kill -9 $PID
        sleep 1
    fi
    echo "✅ Stopped old detection process"
else
    echo "No detection process found"
fi

echo ""
echo "Starting fresh detection..."
echo "=============================="
echo ""

# Start detection
./start_realtime_detection.sh
