#!/bin/bash

# Network Anomaly Detection - Example Anomaly Capture
# This script captures real network traffic and injects example anomalies for demonstration

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "========================================="
echo "  Example Anomaly Capture Mode"
echo "========================================="
echo ""
echo "This mode captures real network traffic and"
echo "injects synthetic anomalies for demonstration."
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    echo "✓ Activating virtual environment..."
    source venv/bin/activate
else
    echo "✗ Virtual environment not found!"
    echo "  Run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if API server is running
if pgrep -f "python api_server.py" > /dev/null; then
    echo "✓ API Server already running on port 5000"
else
    echo "⚠ API Server not running!"
    echo "  Starting API server..."
    python api_server.py > logs/api_server.log 2>&1 &
    sleep 3
    if pgrep -f "python api_server.py" > /dev/null; then
        echo "✓ API Server started on port 5000"
    else
        echo "✗ Failed to start API server"
        exit 1
    fi
fi

# Check if frontend is running
if pgrep -f "next dev" > /dev/null; then
    echo "✓ Frontend already running on port 3000"
else
    echo "⚠ Frontend not running"
    echo "  You can start it manually: cd frontend && npm run dev"
fi

echo ""
echo "========================================="
echo "  Capture Configuration"
echo "========================================="
echo ""
echo "  Interface: wlo1 (WiFi)"
echo "  Backend: PyShark"
echo "  Model: Random Forest"
echo "  Anomaly injection rate: 20%"
echo "  Capture duration: 5 minutes"
echo "  Synthetic delay: 0.5 seconds"
echo ""
echo "Example anomalies that will be generated:"
echo "  • Port scanning patterns"
echo "  • DDoS-like high packet rates"
echo "  • Suspicious protocol usage"
echo "  • Unusual packet sizes"
echo "  • Abnormal connection patterns"
echo ""
echo "========================================="
echo ""
echo "→ Dashboard: http://localhost:3000"
echo "→ Live feed: http://localhost:3000/advanced"
echo "→ Press Ctrl+C to stop detection"
echo ""
echo "Starting capture in 3 seconds..."
sleep 3
echo ""

# Check if another detection is running
if pgrep -f "anomaly_detection.main.*--mode detect" > /dev/null; then
    echo "⚠ Another detection process is running!"
    echo ""
    read -p "Stop existing process and start new one? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Stopping existing process..."
        pkill -f "anomaly_detection.main.*--mode detect"
        sleep 2
    else
        echo "Exiting..."
        exit 0
    fi
fi

# Start detection with anomaly injection
python -m anomaly_detection.main \
    --mode detect \
    --model random_forest \
    --interface wlo1 \
    --backend pyshark \
    --inject-rate 0.2 \
    --duration 300 \
    --synthetic-delay 0.5

echo ""
echo "========================================="
echo "  Detection stopped!"
echo "========================================="
echo ""
echo "View captured anomalies:"
echo "  • Dashboard: http://localhost:3000"
echo "  • Recent detections: Check the Recent Detections panel"
echo "  • Full history: Check data/detections.db"
echo ""
echo "To start real capture (no synthetic anomalies):"
echo "  ./start_realtime_detection.sh"
echo ""
