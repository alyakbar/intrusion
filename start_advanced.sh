#!/bin/bash

# Start All Services Script for Network Anomaly Detection System

echo "🚀 Starting Network Anomaly Detection System with Advanced Features"
echo "=================================================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Install additional dependencies if needed
echo -e "${BLUE}📦 Checking dependencies...${NC}"
pip install -q reportlab requests 2>/dev/null

# Start API Server in background
echo -e "${GREEN}🔧 Starting API Server...${NC}"
python api_server.py > logs/api_server.log 2>&1 &
API_PID=$!
echo "API Server PID: $API_PID (logs: logs/api_server.log)"

# Wait for API to start
sleep 3

# Start Frontend in background
echo -e "${GREEN}🎨 Starting Frontend...${NC}"
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID (logs: logs/frontend.log)"

cd ..

echo ""
echo -e "${GREEN}✅ All services started!${NC}"
echo ""
echo "================================================"
echo "📊 Access Points:"
echo "================================================"
echo "  Frontend:          http://localhost:3000"
echo "  Advanced Features: http://localhost:3000/advanced"
echo "  API Server:        http://localhost:5000"
echo ""
echo "================================================"
echo "🎯 Quick Start Commands:"
echo "================================================"
echo ""
echo "1️⃣  Run Real-Time Detection (PyShark):"
echo "   python anomaly_detection/main.py --mode detect \\"
echo "     --interface wlo1 --backend pyshark \\"
echo "     --inject-rate 0 --duration 999999"
echo ""
echo "2️⃣  Multi-Interface Monitoring:"
echo "   python anomaly_detection/main.py --mode detect \\"
echo "     --interfaces \"wlo1,enp0s25\" --backend pyshark"
echo ""
echo "3️⃣  PCAP Analysis:"
echo "   python anomaly_detection/main.py --mode pcap \\"
echo "     --pcap-file capture.pcap --model random_forest"
echo ""
echo "4️⃣  With Packet Filter:"
echo "   python anomaly_detection/main.py --mode detect \\"
echo "     --interface wlo1 --packet-filter \"tcp port 80\""
echo ""
echo "================================================"
echo "⚙️  Configuration:"
echo "================================================"
echo "  Edit: configs/config.yaml"
echo "  - Enable threat intelligence (AbuseIPDB, VirusTotal)"
echo "  - Configure email alerts (SMTP)"
echo "  - Setup webhook notifications"
echo ""
echo "================================================"
echo "📖 Documentation:"
echo "================================================"
echo "  - ADVANCED_FEATURES.md - Full feature guide"
echo "  - FRONTEND_INTEGRATION.md - Frontend usage"
echo "  - FEATURE_IMPLEMENTATION_SUMMARY.md - Implementation details"
echo ""
echo "================================================"

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stopping services...${NC}"
    kill $API_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Keep script running
wait
