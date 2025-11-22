#!/bin/bash

# Network Anomaly Detection - Quick Start Script
# This script starts packet detection with synthetic data generation

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "========================================="
echo "Network Anomaly Detection - Demo Mode"
echo "========================================="
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
    echo "✗ API Server not running!"
    echo "  Start it in another terminal: python api_server.py"
    exit 1
fi

# Check if frontend is running
if pgrep -f "next dev" > /dev/null; then
    echo "✓ Frontend already running on port 3000"
else
    echo "⚠ Frontend not running"
    echo "  Start it in another terminal: cd frontend && npm run dev"
fi

echo ""
echo "Starting packet detection..."
echo "  • Interface: lo (loopback)"
echo "  • Anomaly injection rate: 30%"
echo "  • Duration: 10 minutes"
echo "  • Packet delay: 0.2 seconds"
echo ""
echo "→ Open dashboard: http://localhost:3000"
echo "→ Press Ctrl+C to stop detection"
echo ""
echo "========================================="
echo ""

# Start detection
python -m anomaly_detection.main \
    --mode detect \
    --model random_forest \
    --interface lo \
    --inject-rate 0.3 \
    --duration 600 \
    --synthetic-delay 0.2

echo ""
echo "========================================="
echo "Detection stopped!"
echo "========================================="
