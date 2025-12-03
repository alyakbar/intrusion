#!/bin/bash
# Start Real-Time Network Anomaly Detection
# This script runs REAL packet capture using PyShark

cd "$(dirname "$0")"

echo "================================================"
echo "🚀 Starting Real-Time Network Anomaly Detection"
echo "================================================"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

echo ""
echo "📡 Configuration:"
echo "   Interface: wlo1 (WiFi)"
echo "   Backend: pyshark (tshark)"
echo "   Mode: Real packet capture (NO synthetic data)"
echo "   Model: Random Forest"
echo ""

# Check if tshark is installed
if ! command -v tshark &> /dev/null; then
    echo "❌ Error: tshark not found. Install with:"
    echo "   sudo apt-get install tshark"
    exit 1
fi

echo "✅ tshark found: $(tshark --version | head -1)"
echo ""

# Check dumpcap permissions
echo "🔐 Checking packet capture permissions..."
if ! timeout 2 tshark -i wlo1 -c 1 &> /dev/null; then
    echo "⚠️  WARNING: Packet capture may need elevated privileges"
    echo ""
    echo "To fix, run these commands once:"
    echo ""
    echo "   sudo groupadd -f wireshark"
    echo "   sudo usermod -aG wireshark \$USER"
    echo "   sudo chgrp wireshark /usr/bin/dumpcap"
    echo "   sudo chmod 750 /usr/bin/dumpcap"
    echo "   sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/dumpcap"
    echo "   newgrp wireshark"
    echo ""
    read -p "Press Enter to continue anyway, or Ctrl+C to abort..."
else
    echo "✅ Packet capture permissions OK"
fi

echo ""
echo "================================================"
echo "🎯 Starting Detection..."
echo "================================================"
echo ""
echo "⏱️  Running indefinitely (Ctrl+C to stop)"
echo "📊 View results at: http://localhost:3000"
echo ""

# Run detection with real packet capture
python anomaly_detection/main.py \
    --mode detect \
    --model random_forest \
    --interface wlo1 \
    --backend pyshark \
    --inject-rate 0 \
    --synthetic-delay 0 \
    --duration 999999

echo ""
echo "🛑 Detection stopped"
